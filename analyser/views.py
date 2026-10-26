from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UploadForm
from .models import Analysis
from .services.analysis import analyse_upload


def upload(request):
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            analysis = analyse_upload(
                form.cleaned_data["resume"],
                form.cleaned_data["job_description"],
                form.cleaned_data["two_column"],
            )
        except ValueError as e:
            form.add_error("resume", str(e))
        else:
            return redirect("detail", pk=analysis.pk)
    return render(request, "analyser/upload.html", {"form": form})


def history(request):
    return render(request, "analyser/history.html", {"analyses": Analysis.objects.all()})


def detail(request, pk):
    return render(request, "analyser/detail.html", {"a": get_object_or_404(Analysis, pk=pk)})


def report(request, pk):
    a = get_object_or_404(Analysis, pk=pk)
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