from .document_parser import extract_document_text
from .section_parser import split_sections
from .scorer import score_resume
from ..models import Analysis


def analyse_upload(file, job_description, two_column=False) -> Analysis:
    """Run the full pipeline and save the result. Raises ValueError with a user-friendly message."""
    try:
        text = extract_document_text(file, two_column=two_column)
    except Exception:
        raise ValueError("Could not read this file.")
    if not text:
        raise ValueError("No text found. A PDF may be a scanned image (OCR needed).")

    result = score_resume(split_sections(text), job_description)
    return Analysis.objects.create(
        filename=file.name,
        job_description=job_description,
        score=result["score"],
        result=result,
    )