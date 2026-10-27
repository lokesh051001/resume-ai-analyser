from rest_framework import filters, viewsets

from .models import JobApplication
from .serializers import JobApplicationSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["company", "role"]

    def get_queryset(self):
        # Only the logged-in user's rows exist as far as this view is concerned,
        # so another user's record is a 404 for every operation, not just for listing.
        queryset = JobApplication.objects.filter(owner=self.request.user)
        status = self.request.query_params.get("status")
        if status:
                    queryset = JobApplication.objects.filter(owner=self.request.user).prefetch_related("analyses")
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)