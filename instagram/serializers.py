from rest_framework import serializers
from .models import InstagramPost

class CaptionSerializer(serializers.Serializer):
    file = serializers.ImageField()
    caption = serializers.CharField()

class NewPostSerializer(serializers.Serializer):
    file = serializers.ImageField()
    caption = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    two_factor_identifier = serializers.CharField(required = False)
    verification_code = serializers.IntegerField(required = False)

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