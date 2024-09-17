from django.db import models
from django.contrib.auth.models import User
from auth_app.models import Bot


class Product(models.Model):
    bot = models.ForeignKey(Bot,on_delete=models.CASCADE)
    product_id = models.CharField(blank=False,max_length=50)
    product_name = models.CharField(blank=False,max_length=100)
    thumbnail = models.ImageField(upload_to='products/thumbnail',blank=True)
    price = models.DecimalField(max_digits=20,decimal_places=2)
    product_img = models.ImageField(upload_to='products/imgs',blank=False)
    product_category = models.CharField(max_length=255,blank=False)
    sub_category = models.CharField(max_length=255,blank=True)
    description = models.CharField(max_length=500,blank=False)
    brand = models.CharField(max_length=100,blank=True)

class ProductDetail(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    option_name = models.CharField(max_length=50)
    option_value = models.CharField(max_length=50)


# class Stock(models.Model):
#     product_id  = models.F
#     redemption_code = 
#     serial_number =
#     expire_date = 
#     status = 
#     date = 
#     sold_to_user


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('completed', 'completed'),
    )

    PAYMENT_CHOICES = (
        ('paypal','paypal'),
        ('stripe','stripe'),
        ('crypto','crypto'),
    )
    bot = models.ForeignKey(Bot,on_delete=models.CASCADE)
    order_date = models.DateField()
    order_number = models.CharField(max_length=255)
    status = models.CharField(max_length=15,choices=STATUS_CHOICES)
    username = models.CharField(max_length=50)
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20)
    email_address= models.EmailField()
    address = models.CharField(max_length=100)
    item_quantity = models.IntegerField()
    payment = models.CharField(max_length=15,choices=PAYMENT_CHOICES)
    order_total = models.DecimalField(max_digits=20,decimal_places=2)
    mail_service = models.CharField(max_length=255)
    discount_code = models.CharField(max_length=255,blank=True)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order,related_name='order_items',on_delete=models.CASCADE)
    # item_name = models.CharField(max_length=255)
