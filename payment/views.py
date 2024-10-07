import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from dotenv import dotenv_values
from rest_framework.views import APIView
from .serializers import PaymentSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from  rest_framework.permissions import IsAuthenticated,BasePermission
from auth_app.permissions import IsInGroupsOrSuperUser

CONFIG = dotenv_values(".env")




class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser]
    def post(self,request):

        payment_serializer = PaymentSerializer(data = request.data)

        if payment_serializer.is_valid():
            payment = Payment.objects.create(**payment_serializer.validated_data)
            
            return Response({'url':request.get_host()+'/create_payment/'+payment.transection_id},status=status.HTTP_200_OK)
        
        return Response(payment_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    def get(self,request):
        dates = self.request.GET.getlist('dates[]')
        # filter_conditions = { }
        # if dates:
        #     start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        #     end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        #     filter_conditions = {
        #     'date_time__gt': start_date,
        #     'date_time__lt': end_date,
        #     }

        payments = Payment.objects.all().order_by('-date_time')
        payments = PaymentSerializer(payments,many=True)

        return Response(payments.data,status=status.HTTP_200_OK)



paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": CONFIG['PAYPAL_CLIENT_ID'],
    "client_secret": CONFIG['PAYPAL_SECRET'],
    "disable-funding":"paylater"
})

def create_payment(request,invoice_id):
    # 127.0.0.1:8000/5c5e2039-1714-4d4c-b687-878497929788
    
    
    invoice = Payment.objects.filter(invoice_id = invoice_id).first()
    if not invoice:
        if invoice.payment_status == "Sucessful":
            return render(request, 'payment_failed.html',{'error_message': 'Duplicate transaction detected. The payment has already been processed.'})
        return render(request, 'payment_failed.html',{'error_message': 'Payment execution failed. Please try again later.'})
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": float(invoice.amount),  # Total amount in USD
                    "currency": "USD",
                },
                "description": invoice.description,
                "invoice_number" : invoice.invoice_id
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'payment_failed.html',{'error_message': 'Payment execution failed. Please try again later.'})
    
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    print(f'Payment ID: {payment_id}')
    print(f'Payer ID: {payer_id}')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        
        
        invoice_number = payment.transactions[0]['invoice_number']
        create_time = payment['transactions'][0]['related_resources'][0]['sale']['create_time']

        # Update the payment record
        Payment.objects.filter(invoice_id=invoice_number).update(
            payments_status="Successful",
            date_time=create_time
        )
        return render(request, 'payment_success.html')
    else:
        error = payment.error
        # print('Payment execution failed.')
        # print(error)
        if error['name'] == 'DUPLICATE_TRANSACTION':
            # Handle duplicate transaction error
            return render(request, 'payment_failed.html', {'error_message': 'Duplicate transaction detected. The payment has already been processed.'})
        else:
            return render(request, 'payment_failed.html', {'error_message': 'Payment execution failed. Please try again later.'})

def payment_checkout(request):
    return render(request, 'checkout.html')

def payment_failed(request):
    return render(request, 'payment_failed.html')


def checkout(request,invoice_id):
    invoice = Payment.objects.filter(invoice_id=invoice_id).first()
    if not invoice:
        if invoice.payment_status == "Sucessful":
            return render(request, 'payment_failed.html',{'error_message': 'Duplicate transaction detected. The payment has already been processed.'})
        return render(request, 'payment_failed.html',{'error_message': 'Payment execution failed. Please try again later.'})
    
    return render(request, 'checkout.html',context={'invoice_id':invoice.invoice_id,'description':invoice.description,'amount':float(invoice.amount)})


# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from .models import Payment

# def get_invoice_details(request, invoice_id):
#     invoice = get_object_or_404(Payment, invoice_id=invoice_id)
#     data = {
#         'invoice_id': invoice.invoice_id,
#         'amount': float(invoice.amount),  # Assuming 'amount' is a DecimalField in your Invoice model
#         'description': invoice.description  # Add other necessary fields
#     }
#     return JsonResponse(data)


