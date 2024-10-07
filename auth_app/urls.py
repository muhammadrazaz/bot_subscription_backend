from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet,UserView,GetUserRoleView,UserBotDetailView,BotDetailViewSet,ForgotPasswordView,ResetPasswordView

routes = DefaultRouter()

routes.register(r"register",RegisterViewSet,basename="register")
routes.register(r"bot-bot-detail",BotDetailViewSet,basename="bot-detail")


urlpatterns = [
    path('api/',include(routes.urls)),
    path('api/user/',UserView.as_view()),
    path('api/user/role/',GetUserRoleView.as_view()),
    path('api/bot-detail/',UserBotDetailView.as_view()),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
   
]