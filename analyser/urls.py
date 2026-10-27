from django.urls import path

from . import api

urlpatterns = [
    path("api/health/", api.health),
    path("api/analyses/", api.analyses_list),
    path("api/analyses/<int:pk>/", api.analysis_detail),
    path("api/analyses/<int:pk>/report/", api.analysis_report),
    path("api/analyse/", api.analyse),
    path("api/suggestions/", api.suggestions),
]