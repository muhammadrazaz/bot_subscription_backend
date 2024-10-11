from django.urls import path,include,re_path
from rest_framework.routers import DefaultRouter
from .views import GenerateCaption,MakePost,PostViewSet,InstagramUser,ConnectInstgramAPIView,SetUpPromptAPIView,DisconnectInstagramApiView,GetPostWaitList,UpdateWaitPost

router = DefaultRouter()

router.register(r'view-posts',PostViewSet,basename='view-posts')

urlpatterns = [
    path('api/generate-caption/',GenerateCaption.as_view()),
    path('api/post-on-instagram/',MakePost.as_view()),
    path('api/instagram/users/',InstagramUser.as_view()),
    path('api/connect-instagram/',ConnectInstgramAPIView.as_view()),
    path('api/set-up-prompt/',SetUpPromptAPIView.as_view()),
    path('api/disconnect-instagram/',DisconnectInstagramApiView.as_view()),
    path('api/instagram/post-wait-list/',GetPostWaitList.as_view()),
    path('api/instagram/update-wait-post/<int:pk>',UpdateWaitPost.as_view()),
    path('api/',include(router.urls)),
]

