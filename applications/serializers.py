from rest_framework import serializers

from .models import JobApplication


class JobApplicationSerializer(serializers.ModelSerializer):
    latest_analysis = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            "id", "company", "role", "status", "applied_date", "interview_date",
            "url", "job_description", "notes", "created_at", "updated_at", "latest_analysis",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "latest_analysis"]

    def get_latest_analysis(self, obj):
        analyses = list(obj.analyses.all())  # newest first, from Meta.ordering
        if not analyses:
            return None
        latest = analyses[0]
        return {"id": latest.pk, "score": latest.score, "created_at": latest.created_at.isoformat()}