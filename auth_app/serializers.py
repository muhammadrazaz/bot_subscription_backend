from rest_framework import serializers
from django.contrib.auth.models import User,Group
from .models import Bot

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.core.mail import send_mail
from django.conf import settings

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(required=True, write_only=True)
#     access_token = serializers.CharField(read_only=True)
#     role = serializers.CharField(read_only=True)

class BotSerializer(serializers.ModelSerializer):
    bot_id = serializers.CharField()
    class Meta:
        model = Bot
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True)
    # first_name = serializers.CharField(required = True)
    # last_name = serializers.CharField(required = True)
    # bot_id = serializers.CharField(required = False,write_only=True)
    # confirm_password = serializers.CharField(required = True,write_only = True)
    # type = serializers.CharField(required= True,write_only=True)
    class Meta:
        model = User
        # fields = ("username","email","first_name","last_name","password","confirm_password","bot_id","type")
        fields = ("username","password")
        


    # def validate(self, attrs):
    #     types = ['subscription','product','pdf','instagram']

    #     if attrs['password'] != attrs['confirm_password'] :
    #         raise serializers.ValidationError({"password":'Password and Confirm Password must be match'})
        
        
    #     # if attrs['type'] not in types:
    #     #     raise serializers.ValidationError({'type':'Type not availble'})
        
    #     # if attrs['type'] == "subscription" or attrs['type'] == "product":
    #     #     if 'bot_id' not in attrs:
    #     #         raise serializers.ValidationError({'bot_id':'This is field is required'})
    #     #     if not Bot.objects.filter(bot_id = attrs['bot_id']).exists():
    #     #         raise serializers.ValidationError({'bot_id':'Bot ID not exist please add valid bot ID'})
        
        
    #     return attrs
    
    def create(self,validated_data):
       
        password =validated_data.pop('password')
        # confirm_password =validated_data.pop('confirm_password')
        # type= validated_data.pop('type')
        type= 'instagram'
        
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        group = Group.objects.get(name=type)

        user.groups.add(group)


        # user_profile = Bot.objects.create(user = user,bot_id = bot_id)
        # user_profile.save()
        if type == "subscription" or type == "product":
            bot_id = validated_data.pop('bot_id')
            bot = Bot.objects.filter(bot_id=bot_id).update(user=user)



        return user
    

class ClientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'


        
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email":"Email not found."})
        return value

    def save(self):
        request = self.context.get('request')
        # print(request.META)
        # 1/0
        # return 
       
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        frontend_url = request.META.get('HTTP_ORIGIN') or request.META.get('HTTP_REFERER')

        reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
        
        # Send an email with the reset link
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"new_password":"Passwords do not match."})
        return data

    def save(self, uidb64, token):
        user_id = urlsafe_base64_decode(uidb64).decode()
        print(user_id)
        user = User.objects.get(pk=user_id)
        print(user,token)

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"confirm_password":"Invalid token or user ID."})
        print('test')
        user.set_password(self.validated_data['new_password'])
        user.save()