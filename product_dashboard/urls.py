from django.urls import path,include

from rest_framework.routers import DefaultRouter
from .views import ProductViewset,ProductCsvUploadView,OrderViewset,ProductDashboardView,ProudctUserApiView,BotProductViewSet,BotOrderViewSet,BotProductCsvUploadView

routes = DefaultRouter()

routes.register(r'products',ProductViewset,basename='product')
routes.register(r'bot-products',BotProductViewSet,basename='bot-product')
routes.register(r'orders',OrderViewset,basename="orders")
routes.register(r'bot-orders',BotOrderViewSet,basename="bot-orders")

urlpatterns =[
   
    path('api/',include(routes.urls)),
    path('api/product-dashboard/',ProductDashboardView.as_view()),
    path('api/upload-product-csv',ProductCsvUploadView.as_view()),
    path('api/bot-upload-product-csv',BotProductCsvUploadView.as_view()),
    path('api/product-clients/',ProudctUserApiView.as_view())
]
