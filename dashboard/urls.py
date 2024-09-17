from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet,DashboardAPIView,UserApiView,ClientDetailViewSet,CsvUploadView

routes = DefaultRouter()


routes.register(r'subscriptions',SubscriptionViewSet,basename="subscriptions")
routes.register(r'client-detail',ClientDetailViewSet,basename="client-detail")


urlpatterns = [
    path("api/",include(routes.urls)),
    path("api/dashboard/",DashboardAPIView.as_view()),
    path('api/clients/',UserApiView.as_view()),
    path('api/upload-csv/',CsvUploadView.as_view())
]