from django.urls import path
from rest_framework.routers import DefaultRouter

from . import dashboard
from .views import JobApplicationViewSet

router = DefaultRouter()
router.register("applications", JobApplicationViewSet, basename="application")

urlpatterns = [path("dashboard/summary/", dashboard.summary)] + router.urls