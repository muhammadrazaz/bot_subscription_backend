from rest_framework import serializers
from .models import InstagramPost,InstagraPostWaitList


class ConnectInstagramSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()
    country_code = serializers.CharField()
    city_name = serializers.CharField()

class CaptionPromptSerializer(serializers.Serializer):
    prompt = serializers.CharField()

class CaptionSerializer(serializers.Serializer):
    file = serializers.ImageField()
    

class NewPostSerializer(serializers.Serializer):
    file = serializers.ImageField()
    caption = serializers.CharField()
    
class PostSerialzer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%d-%m-%Y %I:%M %p')
    class Meta:
        model = InstagramPost
        fields = '__all__'

class InstagramUserDetailSerializer(serializers.Serializer):
     id = serializers.IntegerField()
     web_username = serializers.CharField()
     web_password = serializers.CharField()
     total_post = serializers.CharField()
     first_name = serializers.CharField()
     last_name = serializers.CharField()
     email = serializers.EmailField()

class InstagramPostWaitListSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(read_only = True)
    class Meta:
        model = InstagraPostWaitList
        fields = ['id','caption','file','date_time','time_zone']

class UpdatePostWaitSerializer(serializers.ModelSerializer):
    # date_time = serializers.DateTimeField(read_only = True)
    class Meta:
        model = InstagraPostWaitList
        fields = ['id','caption']



     