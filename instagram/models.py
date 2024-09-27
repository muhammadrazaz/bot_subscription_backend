from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.


class InstagramSession(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    session_data = models.JSONField() 

class ChatGPTPrompt(models.Model):
    user  = models.ForeignKey(User,on_delete=models.CASCADE)
    prompt = models.CharField(max_length=100)

class InstagramPost(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    caption = models.CharField(max_length=500)
    file = models.ImageField('instagram_imgs')
    post_url = models.URLField()
    date_time = models.DateTimeField(default=datetime.now())
