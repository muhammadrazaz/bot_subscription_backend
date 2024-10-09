from django.db import models
from  django.contrib.auth.models import User



class Bot(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE,blank=True,null=True)
    bot_id = models.CharField(max_length=50,blank=False,unique=True)
    telegram_username = models.CharField(max_length=50,blank=False)
    bot_father_token = models.CharField(max_length=255,blank=False)
    bot_url = models.CharField(max_length=255,blank=False)
    server_username = models.CharField(max_length=255,blank=True)
    server_password = models.CharField(max_length=255,blank=True)
    instance_dns = models.CharField(max_length=255,blank=True)
    instance_username = models.CharField(max_length=255,blank=True,default='')
    instance_password = models.CharField(max_length=255,blank=True)
    database_backup = models.FileField(upload_to='backup',blank=True,null=True)
    type  = models.CharField(max_length=50,blank=False)


    #product upload done
    #product upload from file
    #product fetch done
    #order upload and fetch done
    #user profile done
    #local database backup done

    def __str__(self) -> str:
        return str(self.id)
