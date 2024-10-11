from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.


class InstagramSession(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    session_data = models.JSONField()
    proxy = models.CharField(max_length=300,default='')

class ChatGPTPrompt(models.Model):
    user  = models.ForeignKey(User,on_delete=models.CASCADE)
    prompt = models.CharField(max_length=100)

class InstagramPost(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    caption = models.CharField(max_length=500)
    file = models.ImageField(upload_to='instagram_imgs')
    post_url = models.URLField()
    date_time = models.DateTimeField(default=datetime.now())


class InstagraPostWaitList(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    caption = models.CharField(max_length=500)
    file = models.ImageField(upload_to='instagram_imgs')
    date_time = models.DateTimeField()
    time_zone = models.CharField(max_length=50)
    task_id = models.CharField(max_length=255, null=True, blank=True)

class PostWithProblem(models.Model):
    data = models.JSONField()
    error = models.CharField(max_length=5000)
