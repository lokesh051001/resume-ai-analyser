from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload, name="upload"),
    path("history/", views.history, name="history"),
    path("analysis/<int:pk>/", views.detail, name="detail"),
    path("analysis/<int:pk>/report/", views.report, name="report"),
]