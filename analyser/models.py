from django.conf import settings
from django.db import models


class Analysis(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="analyses", null=True, blank=True,
    )
    application = models.ForeignKey(
        "applications.JobApplication", on_delete=models.SET_NULL,
        related_name="analyses", null=True, blank=True,
    )
    filename = models.CharField(max_length=255)
    job_description = models.TextField()
    score = models.FloatField()
    result = models.JSONField()  # the full breakdown dict from score_resume
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.score})"