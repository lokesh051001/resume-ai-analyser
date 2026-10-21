from django.shortcuts import render, redirect, get_object_or_404

from .forms import UploadForm
from .models import Analysis
from .services.pdf_parser import extract_text
from .services.section_parser import split_sections
from .services.scorer import score_resume
from django.http import HttpResponse

def upload(request):
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        f = form.cleaned_data["resume"]
        job = form.cleaned_data["job_description"]
        try:
            text = extract_text(f, two_column=form.cleaned_data["two_column"])
        except Exception:
            form.add_error("resume", "Could not read this PDF.")
        else:
            if not text:
                form.add_error("resume", "No text found. This may be a scanned image (OCR needed).")
            else:
                result = score_resume(split_sections(text), job)
                analysis = Analysis.objects.create(
                    filename=f.name,
                    job_description=job,
                    score=result["score"],
                    result=result,
                )
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
        "Required skills missing: " + (", ".join(r["required_missing"]) or "none"),
        "Preferred skills missing: " + (", ".join(r["preferred_missing"]) or "none"),
        "Listed but not demonstrated: " + (", ".join(r["not_demonstrated"]) or "none"),
    ]
    response = HttpResponse("\n".join(lines), content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="report_{a.pk}.txt"'
    return response
