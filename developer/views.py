from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from django.db.models import Sum,Count
from django.db.models.functions import Coalesce
# Create your views here.

class ProjectAPIView(APIView):

    def post(self, request):
        project_serilalizer = ProjectSerializer(data = request.data)

        if project_serilalizer.is_valid():
            data = project_serilalizer.validated_data
            project = Project.objects.create(**data)
            return Response({'message':'success'},status=status.HTTP_201_CREATED)
        
        return Response(project_serilalizer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        projects = Project.objects.filter().annotate(
            total_cost =Coalesce(Sum('task__task_cost'),0),
            total_tasks =Coalesce(Count('task__id'),0),
            total_developers=Coalesce(Count('task__developer_id', distinct=True), 0)
            )
        projects = ProjectSerializer(projects,many=True)
        return Response({'projects' : projects.data},status=status.HTTP_200_OK)