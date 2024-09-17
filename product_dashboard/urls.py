from django.urls import path,include

from rest_framework.routers import DefaultRouter
from .views import ProductViewset,ProductCsvUploadView,OrderViewset,ProductDashboardView,ProudctUserApiView

routes = DefaultRouter()

routes.register(r'products',ProductViewset,basename='product')
routes.register(r'orders',OrderViewset,basename="orders")

urlpatterns =[
   
    path('api/',include(routes.urls)),
    path('api/product-dashboard/',ProductDashboardView.as_view()),
    path('api/upload-product-csv',ProductCsvUploadView.as_view()),
    path('api/product-clients/',ProudctUserApiView.as_view())
]
