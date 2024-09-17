from django.urls import path,include
from .views import PDFAPIView,DownloadZipView,PDFUser

urlpatterns =[
    path('api/pdf/',PDFAPIView.as_view()),
    path('api/pdf/download/',DownloadZipView.as_view()),
    path('api/pdf/users',PDFUser.as_view())
]