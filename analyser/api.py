from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import UploadForm
from .models import Analysis
from .services.analysis import analyse_upload


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