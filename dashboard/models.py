from django.db import models

from auth_app.models import Bot


class Subscription(models.Model):
    bot = models.ForeignKey(Bot,on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255,blank=False)
    username = models.CharField(max_length=255,blank=False)
    name = models.CharField(max_length=255,blank=False)
    status = models.BooleanField(blank=False)
    payment = models.CharField(max_length=255,blank=False)
    cancelled = models.BooleanField(blank=False)
    subscription_id = models.CharField(max_length=255,blank=False)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    plan = models.CharField(max_length=255,blank=False)
    plan_id = models.IntegerField()
    price = models.IntegerField(blank=False)


