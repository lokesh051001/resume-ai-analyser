from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import UploadForm
from .models import Analysis
from .services.analysis import analyse_upload
from .services.pdf_parser import extract_text
from .services.section_parser import split_sections
from .services.scorer import score_resume
from .services.suggestions import SuggestionError, create_suggestions
from django.conf import settings
from django.core.cache import cache


def _serialize(a):
    return {
        "id": a.pk,
        "filename": a.filename,
        "score": a.score,
        "created_at": a.created_at.isoformat(),
        "result": a.result,
    }


@require_GET
def analyses_list(request):
    return JsonResponse({"analyses": [_serialize(a) for a in Analysis.objects.all()]})


@require_GET
def analysis_detail(request, pk):
    return JsonResponse(_serialize(get_object_or_404(Analysis, pk=pk)))


@csrf_exempt  # fine for local learning; revisit when we add login
@require_POST
def analyse(request):
    form = UploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"errors": {k: list(v) for k, v in form.errors.items()}}, status=400)
    try:
        a = analyse_upload(
            form.cleaned_data["resume"],
            form.cleaned_data["job_description"],
            form.cleaned_data["two_column"],
        )
    except ValueError as e:
        return JsonResponse({"errors": {"resume": [str(e)]}}, status=400)
    return JsonResponse(_serialize(a), status=201)


@csrf_exempt
@require_POST
def suggestions(request):
    origin = request.headers.get("Origin")
    if origin and origin not in settings.CORS_ALLOWED_ORIGINS:
        return JsonResponse({"error": "Request origin is not allowed."}, status=403)
    if not settings.CLAUDE_SUGGESTIONS_ENABLED or not settings.ANTHROPIC_API_KEY:
        return JsonResponse({"error": "AI suggestions are disabled. Configure the Claude API key and enable the feature in .env."}, status=503)

    # Five requests per client address per hour; cache storage can be replaced
    # with a shared backend when deploying more than one worker.
    address = request.META.get("REMOTE_ADDR", "unknown")
    key = f"claude-suggestions:{address}"
    try:
        count = cache.get(key, 0)
        if count >= 5:
            return JsonResponse({"error": "Suggestion limit reached. Try again in an hour."}, status=429)
        cache.set(key, count + 1, timeout=3600)
    except Exception:
        pass

    form = UploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"errors": {k: list(v) for k, v in form.errors.items()}}, status=400)
    try:
        sections = split_sections(extract_text(form.cleaned_data["resume"], form.cleaned_data["two_column"]))
        score = score_resume(sections, form.cleaned_data["job_description"])
        result = create_suggestions(sections, score["required_missing"] + score["preferred_missing"], score["not_demonstrated"])
        return JsonResponse(result)
    except SuggestionError as e:
        return JsonResponse({"error": str(e)}, status=502)
    except Exception:
        return JsonResponse({"error": "Could not prepare suggestions. Your analysis is still available."}, status=400)
