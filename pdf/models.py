from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.


class PDFFiles(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    input  = models.CharField(max_length=255)
    output = models.CharField(max_length=255)
    output_with_contacts = models.CharField(max_length=255,default='')
    date_time = models.DateTimeField(default=datetime.now)