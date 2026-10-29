from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from analyser.models import Analysis

from .models import JobApplication


@api_view(["GET"])
def summary(request):
    apps = JobApplication.objects.filter(owner=request.user)

    counts = {status: 0 for status in JobApplication.Status.values}
    for row in apps.values("status").annotate(n=Count("id")):
        counts[row["status"]] = row["n"]

    upcoming = (
        apps.filter(interview_date__gte=timezone.now())
        .exclude(status__in=["rejected", "withdrawn"])
        .order_by("interview_date")[:5]
    )
    recent = Analysis.objects.filter(owner=request.user)[:5]

    return Response({
        "total": apps.count(),
        "by_status": counts,
        "upcoming_interviews": [
            {"id": a.pk, "company": a.company, "role": a.role, "interview_date": a.interview_date.isoformat()}
            for a in upcoming
        ],
        "recent_analyses": [
            {"id": a.pk, "filename": a.filename, "score": a.score,
             "created_at": a.created_at.isoformat(), "application": a.application_id}
            for a in recent
        ],
    })