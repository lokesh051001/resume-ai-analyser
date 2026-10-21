from django.db import models


class Analysis(models.Model):
    filename = models.CharField(max_length=255)
    job_description = models.TextField()
    score = models.FloatField()
    result = models.JSONField()  # the full breakdown dict from score_resume
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.filename} ({self.score})"