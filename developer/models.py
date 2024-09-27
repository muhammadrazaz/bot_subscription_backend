from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
# Create your models here.
def validate_file_size(value):
    filesize = value.size
    
   
    megabyte_limit = 50
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"Maximum file size is {megabyte_limit}MB")
    


class Project(models.Model):
    project_name = models.CharField(max_length=50)


class Task(models.Model):
    stutus_choices = [('open','Open'),('started','Started'),('completed','Completed')]

    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    task_detail = models.CharField(max_length=30)
    task_detail_video = models.FileField(upload_to='task/task_detail_video',blank=True,null=True,validators=[validate_file_size])
    requirement_document = models.FileField(upload_to='task_requirement_document',validators=[validate_file_size])
    task_timeline = models.CharField(max_length=30)
    task_cost = models.IntegerField()
    instruction_video = models.FileField(upload_to='task/instruction_video',blank=True,null=True,validators=[validate_file_size])
    code_explanation_video = models.FileField(upload_to='task/code_explanation_video',blank=True,null=True,validators=[validate_file_size])
    lastest_files = models.FileField(upload_to='task/code_explanation_video',blank=True,null=True,validators=[validate_file_size])
    status = models.CharField(max_length=30,choices=stutus_choices,default='open')
    remarks = models.CharField(max_length=30,blank=True,null=True)
    developer = models.ForeignKey(User,on_delete=models.DO_NOTHING)

