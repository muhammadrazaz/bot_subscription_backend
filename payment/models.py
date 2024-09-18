from django.db import models
import uuid
# Create your models here.

payment_status_choices = (('Pending','pending'),('Successful','successful'))

class Payment(models.Model):
    invoice_id = models.CharField(max_length=100,default=str(uuid.uuid4()))
    client_name = models.CharField(max_length=50)
    client_email = models.EmailField()
    address = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    amount = models.DecimalField(decimal_places=2,max_digits=10)
    misc_details = models.CharField(max_length=100)
    payment_status = models.CharField( max_length=50,choices=payment_status_choices,default='Pending')
    date_time  = models.DateTimeField(blank=True,null=True)