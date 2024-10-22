from rest_framework import serializers
from .models import Project,Task
from django.contrib.auth.models import User
import os
class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    project_name = serializers.CharField(max_length = 50)
    total_cost = serializers.IntegerField(read_only = True)
    total_tasks = serializers.IntegerField(read_only = True)
    total_developers = serializers.IntegerField(read_only = True)
    latest_files = serializers.FileField(read_only =True)
    date = serializers.DateField()


    def validate(self, attrs):
        attrs = super().validate(attrs)
        
        if Project.objects.filter(project_name = attrs['project_name']).exists():
            raise serializers.ValidationError({"project_name":'Project name already exists'})
        return attrs
    
class TaskSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, attrs):
        
        if 'task_detail_video' in attrs:
            if not attrs['task_detail_video']:
                attrs.pop('task_detail_video')
            else:
                valid_extensions = ['.mp4', '.avi', '.mov']
                ext = os.path.splitext(attrs['task_detail_video'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError("Unsupported file extension. Allowed: "+', '.join(valid_extensions))
        if 'requirement_document' in attrs:    
            if not attrs['requirement_document']:
                attrs.pop('requirement_document')
            else:
                valid_extensions = ['.doc', '.docx',]
                ext = os.path.splitext(attrs['requirement_document'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError("Unsupported file extension. Allowed: "+', '.join(valid_extensions))
        if 'instruction_video' in attrs:    
            if not attrs['instruction_video']:
                attrs.pop('instruction_video')
            else:
                valid_extensions = ['.mp4', '.avi', '.mov']
                ext = os.path.splitext(attrs['instruction_video'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError("Unsupported file extension. Allowed: "+', '.join(valid_extensions))
        if 'code_explanation_video' in attrs:    
            if not attrs['code_explanation_video']:
                attrs.pop('code_explanation_video')
            else:
                valid_extensions = ['.mp4', '.avi', '.mov']
                ext = os.path.splitext(attrs['code_explanation_video'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError("Unsupported file extension. Allowed: "+', '.join(valid_extensions))
        if 'latest_files' in attrs:    
            if not attrs['latest_files']:
                attrs.pop('latest_files')
            else:
                valid_extensions = ['.zip']
                ext = os.path.splitext(attrs['latest_files'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError("Unsupported file extension. Allowed: "+', '.join(valid_extensions))
        
        return super().validate(attrs)
    

    def create(self, validated_data):
        
        id = validated_data.pop('id', None)

        # If 'id' is provided, try to update; otherwise, create a new instance
        if id:
            # Update if the id exists
            task, created = Task.objects.update_or_create(id=id, defaults=validated_data)
        else:
            # Create a new instance if no id is provided
            task = Task.objects.create(**validated_data)
        return task

    # def get_fields(self):
    #     fields =  super().get_fields()
    #     request = self.context.get('request')
    #     if request.user.is_superuser:
    #         fields['developer'].read_only = False
    #     else:
    #         fields['developer'].read_only = True



class OpenTaskSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField(read_only = True)
    id = serializers.IntegerField()
    class Meta:
        model = Task
        fields = ['id','task_detail','task_detail_video','requirement_document','task_timeline','task_cost','remarks','project','developer','projects']

    def validate(self, attrs):
        if 'task_detail_video' in attrs:
            if not attrs['task_detail_video']:
                attrs.pop('task_detail_video')
            else:
                valid_extensions = ['.mp4', '.avi', '.mov']
                ext = os.path.splitext(attrs['task_detail_video'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError({"task_detail_video":"Unsupported file extension. Allowed: "+', '.join(valid_extensions)})
            
        

        if 'requirement_document' in attrs:
            if not attrs['requirement_document']:
                attrs.pop('requirement_document')
            else:
                valid_extensions = ['.doc', '.docx',]
                ext = os.path.splitext(attrs['requirement_document'].name)[1].lower()
                if ext not in valid_extensions:
                    raise serializers.ValidationError({"requirement_document":"Unsupported file extension. Allowed: "+', '.join(valid_extensions)})
        if 'developer' in attrs:       
            if attrs['developer']:
                attrs['status'] = "started"
            
        # return attrs
        return super().validate(attrs)
    

    def get_projects(self, obj):
        projects = Project.objects.all()
        return [self.project_to_json(project) for project in projects]

    def project_to_json(self, project):
        # Convert individual project object to JSON format
        return {
            'id': project.id,
            'project_name': project.project_name,
            
        }
    
    def create(self, validated_data):
        
        id = validated_data.pop('id', None)

        # If 'id' is provided, try to update; otherwise, create a new instance
        if id:
            # Update if the id exists
            task, created = Task.objects.update_or_create(id=id, defaults=validated_data)
        else:
            # Create a new instance if no id is provided
            task = Task.objects.create(**validated_data)
        return task
    


class DeveloperSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'