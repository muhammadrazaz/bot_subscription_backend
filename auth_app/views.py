from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import RegisterSerializer,BotSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Bot

class UserView(APIView):
   
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user

        group = user.groups.first()
        
        if group or user.is_superuser:
            return Response({"name":user.first_name+" "+user.last_name,"role":"admin" if user.is_superuser else group.name,"user_id":user.id}, status=status.HTTP_200_OK)
        return Response({"name":user.first_name+" "+user.last_name,"role":""}, status=status.HTTP_200_OK)  

class RegisterViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    http_method_names = ['post']


class GetUserRoleView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        id = request.query_params.get('user_id')
        user = User.objects.get(pk=id)
        group = user.groups.first()
        if group:
            return Response({'role':group.name})
        return Response({'role':''})
    

class UserBotDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = BotSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            update,create = Bot.objects.update_or_create(
                bot_id = data['bot_id'],
                defaults={'telegram_username':data['telegram_username'],'bot_father_token':data['bot_father_token'],'bot_url':data['bot_url'],'database_backup':data['database_backup']}
            )
            
            if create:
                return Response({'message':'successfully created'},status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'successfully updated'},status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
