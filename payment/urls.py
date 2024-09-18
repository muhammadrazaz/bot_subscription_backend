from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import payment_checkout,checkout,create_payment,execute_payment,payment_failed,PaymentAPIView

routes = DefaultRouter()



urlpatterns = [
    path('checkout/<str:invoice_id>/', checkout, name='checkout_payment'),
    path('create_payment/<str:invoice_id>/', create_payment, name='create_payment'),
    path('execute_payment/', execute_payment, name='execute_payment'),
    path('payment_failed/', payment_failed, name='payment_failed'),
    path('api/payment/',PaymentAPIView.as_view())
]