from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProjectAPIView


urlpatterns = [
    path('api/developer/project/',ProjectAPIView.as_view())
]