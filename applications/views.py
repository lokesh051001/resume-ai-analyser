from rest_framework import filters, viewsets

from .models import JobApplication
from .serializers import JobApplicationSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["company", "role"]

    def get_queryset(self):
        queryset = JobApplication.objects.filter(owner=self.request.user).prefetch_related("analyses")
        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
