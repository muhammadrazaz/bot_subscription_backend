from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import RegisterSerializer,BotSerializer,ForgotPasswordSerializer,ResetPasswordSerializer,ClientDetailSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Bot
from rest_framework.exceptions import NotFound
from rest_framework import generics


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
        id = request.query_params.get('bot_id')
        type = Bot.objects.get(pk=id).type
        # group = user.groups.first()
        if type:
            return Response({'role':type.name})
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
    
class ClientDetailViewSet(viewsets.ModelViewSet):
    serializer_class = ClientDetailSerializer
    # permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['subscription','VA'])]
    

    def get_queryset(self):
        queryset = Bot.objects.all()
        # return queryset
        
        bot_id = self.request.query_params.get('bot_id')
        if bot_id:
            obj = queryset.filter(pk=bot_id)
            return obj
        return queryset
    
    

class BotDetailViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer
    queryset = Bot.objects.all()

    def get_object(self):
    
        bot_id = self.kwargs.get('pk')
        try:
            
            return Bot.objects.get(bot_id=bot_id)
        except Bot.DoesNotExist:
            
            raise NotFound("Bot with the given bot_id does not exist")




class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(uidb64, token)
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




