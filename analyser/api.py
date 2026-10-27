import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from applications.models import JobApplication

from .forms import UploadForm
from .models import Analysis
from .services.analysis import analyse_upload
from .services.document_parser import extract_document_text
from .services.scorer import score_resume
from .services.section_parser import split_sections
from .services.suggestions import SuggestionError, create_suggestions


def _serialize(a):
    return {
        "id": a.pk,
        "filename": a.filename,
        "score": a.score,
        "created_at": a.created_at.isoformat(),
        "application": a.application_id,
        "result": a.result,
    }


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "message": "Resume analyser API is running"})


@api_view(["GET"])
def analyses_list(request):
    queryset = Analysis.objects.filter(owner=request.user)
    application = request.query_params.get("application")
    if application and application.isdigit():
        queryset = queryset.filter(application_id=int(application))
    return Response({"analyses": [_serialize(a) for a in queryset]})


@api_view(["GET"])
def analysis_detail(request, pk):
    return Response(_serialize(get_object_or_404(Analysis, pk=pk, owner=request.user)))


@api_view(["GET"])
def analysis_report(request, pk):
    a = get_object_or_404(Analysis, pk=pk, owner=request.user)
    r = a.result
    lines = [
        "RESUME ANALYSIS REPORT",
        "=" * 30,
        f"File: {a.filename}",
        f"Date: {a.created_at:%Y-%m-%d %H:%M}",
        f"Overall score: {a.score}/100",
        "",
        "Score breakdown:",
    ]
    lines += [f"  - {name}: {value}" for name, value in r["breakdown"].items()]
    lines += [
        "",
        "Required skills matched: " + (", ".join(r.get("required_matched", [])) or "none"),
        "Required skills missing: " + (", ".join(r["required_missing"]) or "none"),
        "Preferred skills missing: " + (", ".join(r["preferred_missing"]) or "none"),
        "Listed but not demonstrated: " + (", ".join(r["not_demonstrated"]) or "none"),
    ]
    response = HttpResponse("\n".join(lines), content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="report_{a.pk}.txt"'
    return response


def _linked_application(request):
    """Return (application, error_response). The application must belong to the logged-in user."""
    app_id = request.POST.get("application")
    if not app_id:
        return None, None
    if not app_id.isdigit():
        return None, Response({"errors": {"application": ["Invalid application."]}}, status=400)
    application = JobApplication.objects.filter(owner=request.user, pk=int(app_id)).first()
    if application is None:
        return None, Response({"errors": {"application": ["Application not found."]}}, status=404)
    return application, None


@api_view(["POST"])
def analyse(request):
    application, error = _linked_application(request)
    if error:
        return error

    data = request.POST.copy()
    if application and not data.get("job_description", "").strip():
        data["job_description"] = application.job_description

    form = UploadForm(data, request.FILES)
    if not form.is_valid():
        return Response({"errors": {k: list(v) for k, v in form.errors.items()}}, status=400)
    try:
        a = analyse_upload(
            form.cleaned_data["resume"],
            form.cleaned_data["job_description"],
            form.cleaned_data["two_column"],
            owner=request.user,
            application=application,
        )
    except ValueError as e:
        return Response({"errors": {"resume": [str(e)]}}, status=400)
    return Response(_serialize(a), status=201)


@api_view(["POST"])
def suggestions(request):
    origin = request.headers.get("Origin")
    if origin and origin not in settings.CORS_ALLOWED_ORIGINS:
        return Response({"error": "Request origin is not allowed."}, status=403)
    if not settings.CLAUDE_SUGGESTIONS_ENABLED or not settings.ANTHROPIC_API_KEY:
        return Response(
            {"error": "AI suggestions are disabled. Configure the Claude API key and enable the feature in .env."},
            status=503,
        )

    form = UploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return Response({"errors": {k: list(v) for k, v in form.errors.items()}}, status=400)

    # Five valid requests per user per hour. Cache storage can be replaced
    # with a shared backend when deploying more than one worker.
    key = f"claude-suggestions:{request.user.pk}"
    try:
        count = cache.get(key, 0)
        if count >= 5:
            return Response({"error": "Suggestion limit reached. Try again in an hour."}, status=429)
        cache.set(key, count + 1, timeout=3600)
    except Exception:
        logging.exception("Rate limit cache unavailable")

    try:
        sections = split_sections(
            extract_document_text(form.cleaned_data["resume"], form.cleaned_data["two_column"])
        )
        score = score_resume(sections, form.cleaned_data["job_description"])
        result = create_suggestions(
            sections,
            score["required_missing"] + score["preferred_missing"],
            score["not_demonstrated"],
        )
        return Response(result)
    except SuggestionError as e:
        return Response({"error": str(e)}, status=502)
    except Exception:
        logging.exception("Suggestion preparation failed")
        return Response(
            {"error": "Could not prepare suggestions. Your analysis is still available."},
            status=500,
        )