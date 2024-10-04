from  rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    invoice_id = serializers.CharField(read_only = True)
    payment_status = serializers.CharField(read_only = True)
    class Meta:
        model = Payment
        fields = ('invoice_id','client_name','client_email','address','description','amount','misc_details','payment_status')