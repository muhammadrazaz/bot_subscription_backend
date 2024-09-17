from rest_framework import serializers
from django.contrib.auth.models import User,Group
from .models import Bot

from rest_framework import serializers

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
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required = True)
    last_name = serializers.CharField(required = True)
    bot_id = serializers.CharField(required = True,write_only=True)
    confirm_password = serializers.CharField(required = True,write_only = True)
    type = serializers.CharField(required= True,write_only=True)
    class Meta:
        model = User
        fields = ("username","email","first_name","last_name","password","confirm_password","bot_id","type")
        


    def validate(self, attrs):
        types = ['subscription','product']

        if attrs['password'] != attrs['confirm_password'] :
            raise serializers.ValidationError({"password":'Password and Confirm Password must be match'})
        if not Bot.objects.filter(bot_id = attrs['bot_id']).exists():
            raise serializers.ValidationError({'bot':'Bot ID not exist please add valid bot ID'})
        
        if attrs['type'] not in types:
            raise serializers.ValidationError({'type':'Type not availble'})
        
        
        return attrs
    
    def create(self,validated_data):
        bot_id = validated_data.pop('bot_id')
        password =validated_data.pop('password')
        confirm_password =validated_data.pop('confirm_password')
        type= validated_data.pop('type')
        
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        group = Group.objects.get(name=type)

        user.groups.add(group)


        # user_profile = Bot.objects.create(user = user,bot_id = bot_id)
        # user_profile.save()

        bot = Bot.objects.filter(bot_id=bot_id).update(user=user)



        return user