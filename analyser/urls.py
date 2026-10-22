from django.urls import path
from . import views, api

urlpatterns = [
    path("", views.upload, name="upload"),
    path("history/", views.history, name="history"),
    path("analysis/<int:pk>/", views.detail, name="detail"),
    path("analysis/<int:pk>/report/", views.report, name="report"),
    path("api/analyses/", api.analyses_list),
    path("api/analyses/<int:pk>/", api.analysis_detail),
    path("api/analyse/", api.analyse),
]