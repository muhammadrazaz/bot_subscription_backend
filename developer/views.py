from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import viewsets
from .serializers import ProjectSerializer,TaskSerializer,OpenTaskSerializer,DeveloperSerilaizer
from rest_framework.response import Response
from rest_framework import status
from .models import Project,Task
from django.db.models import Sum,Count,Max
from django.db.models.functions import Coalesce
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission,IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime
from auth_app.permissions import IsInGroupsOrSuperUser
# Create your views here.


# class IsDevleloperOrVAOrSuperUser(BasePermission):
   
#     def has_permission(self, request, view):
#         # Check if the user is authenticated
#         if not request.user or not request.user.is_authenticated:
#             return False
#         group = request.user.groups.first() 
#         if (group and group.name == "developer") or (group and group.name == "VA")  or request.user.is_superuser:
#             return True
#         else:
#             return False

class ProjectAPIView(APIView):

    def post(self, request):
        project_serilalizer = ProjectSerializer(data = request.data)

        if project_serilalizer.is_valid():
            data = project_serilalizer.validated_data
            project = Project.objects.create(**data)
            return Response({'message':'success'},status=status.HTTP_201_CREATED)
        
        return Response(project_serilalizer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        dates = self.request.GET.getlist('dates[]')
        filter_conditions = {}
        if dates:
            start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            filter_conditions = {
            'date__gte': start_date,
            'date__lte': end_date,
            }
        if request.user.groups.filter(name="developer").exists():
            filter_conditions['task__developer'] = request.user
        projects = Project.objects.filter(**filter_conditions).annotate(
            total_cost =Coalesce(Sum('task__task_cost'),0),
            total_tasks =Coalesce(Count('task__id'),0),
            total_developers=Coalesce(Count('task__developer_id', distinct=True), 0),
            latest_files= Max('task__requirement_document') 
            ).order_by('-date')
       
        projects = ProjectSerializer(projects,many=True)
        return Response({'projects' : projects.data},status=status.HTTP_200_OK)
    
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['developer','VA'])]
    
    queryset = Task.objects.filter(~Q(status='open'))

    def get_queryset(self):
        queryset = self.queryset
        project_id = self.request.query_params.get('project_id')

        filter_condition = {
            'project_id':project_id,
        }
        if self.request.user.groups.filter(name="developer").exists():
            filter_condition['developer'] = self.request.user
        queryset = queryset.filter(**filter_condition)
        return queryset
    

class OpenTaskViewSet(viewsets.ModelViewSet):
    serializer_class = OpenTaskSerializer
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['developer','VA'])]
    queryset = Task.objects.filter(status="open")


class DeveloperViewSet(viewsets.ModelViewSet):
    serializer_class = DeveloperSerilaizer
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['developer','VA'])]
    queryset = User.objects.filter(groups__name = 'developer')
    http_method_names = ('get')

    