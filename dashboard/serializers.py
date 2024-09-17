from rest_framework import serializers
from .models import Subscription
from django.contrib.auth.models import User
from auth_app.models import Bot
import pandas as pd
class SubscriptionSerializer(serializers.ModelSerializer):
    cancelled_str = serializers.CharField( read_only=True)
    status_str = serializers.CharField( read_only=True)
    bot = serializers.CharField(required = True)
    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, attrs):
        bot = Bot.objects.filter(bot_id = attrs['bot']).first()
        if not bot:
            raise serializers.ValidationError({'bot':"bot id is not valid"})
        else:
            attrs['bot'] = bot
        return super().validate(attrs)



class UserDetailSerializer(serializers.Serializer):
     id = serializers.IntegerField()
     web_username = serializers.CharField()
     web_password = serializers.CharField()
    #  order_id = serializers.CharField()
    #  order_date = serializers.DateField()
     total_earnings = serializers.CharField()
     total_users = serializers.IntegerField()

class ClientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'


class CsvUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate(self, attrs):
      
        if not attrs['file'].name.endswith('.csv'):
            raise serializers.ValidationError({'file':"Only CSV files are allowed."})
        
        file = attrs['file']
        file.seek(0)  # Reset file pointer to the beginning

        
        df = pd.read_csv(attrs['file'])
        if 'bot_id' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain bot_id column."})
        if 'telegram_username' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain telegram_username column."})
        if 'bot_father_token' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain bot_father_token column."})
        if 'bot_url' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain bot_url column."})
        if 'server_username' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain server_username column."})
        if 'server_password' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain server_password column."})
        if 'instance_dns' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain instance_dns column."})
        if 'instance_password' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain instance_password column."})
        if 'instance_username' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain instance_username column."})
       
        
        empty_column = df.columns[df.isnull().any()].tolist()
        
        
        if len(empty_column):
            raise serializers.ValidationError({'file':' ,'.join(empty_column)+" contain null please fill all."})
            
        return attrs
    

      