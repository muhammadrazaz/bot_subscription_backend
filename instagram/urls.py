from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import GenerateCaption,MakePost,PostViewSet,InstagramUser

router = DefaultRouter()

router.register(r'view-posts',PostViewSet,basename='view-posts')

urlpatterns = [
    path('api/generate-caption/',GenerateCaption.as_view()),
    path('api/post-on-instagram/',MakePost.as_view()),
    path('api/instagram/users/',InstagramUser.as_view()),
    path('api/',include(router.urls))
]