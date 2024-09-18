from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet,UserView,GetUserRoleView,UserBotDetailView

routes = DefaultRouter()

routes.register(r"register",RegisterViewSet,basename="register")


urlpatterns = [
    path('api/',include(routes.urls)),
    path('api/user/',UserView.as_view()),
    path('api/user/role/',GetUserRoleView.as_view()),
    path('api/bot-detail/',UserBotDetailView.as_view()),
   
]