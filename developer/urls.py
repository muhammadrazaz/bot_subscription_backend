from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProjectAPIView,TaskViewSet,OpenTaskViewSet,DeveloperViewSet


routes = DefaultRouter()

routes.register(r'developer/project/detail',TaskViewSet,basename='task-detail')
routes.register(r'developer/open-task',OpenTaskViewSet,basename='open-task')
routes.register(r'developers',DeveloperViewSet)


urlpatterns = [
    path('api/',include(routes.urls)),
    path('api/developer/project/',ProjectAPIView.as_view()),
    
]