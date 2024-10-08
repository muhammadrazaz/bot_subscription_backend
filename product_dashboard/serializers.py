from rest_framework import serializers
from .models import Product,Order,OrderItem
from auth_app.models import Bot
from io import StringIO
import csv
import pandas as pd

class ProductSerializer(serializers.ModelSerializer):
    bot = serializers.CharField(required=False)
    thumbnail = serializers.ImageField(required=False)
    # product_img = serializers.ImageField(required = False)
    class Meta:
        model = Product
        fields = '__all__'
    def validate(self, attrs):
        request = self.context.get('request')
        
        # if request.method == 'POST' and 'thumbnail' not in attrs:
        #     raise serializers.ValidationError({"thumbnail": "This field is required."})
        if request.method == 'POST' and 'product_img' not in attrs:
            raise serializers.ValidationError({"product_img": "This field is required."})
        if 'bot' in attrs:
            bot = Bot.objects.get(bot_id = bot)
        else:
            bot = Bot.objects.get(user=request.user)
        attrs['bot'] = bot
        return super().validate(attrs)
        





class OrderSerializer(serializers.ModelSerializer):
    
    items = serializers.ListField(write_only = True)
    order_items = serializers.SerializerMethodField(read_only = True)
    bot = serializers.CharField(required = True)
    class Meta:
        model = Order
        fields = '__all__'


    def validate(self, attrs):


        if not Bot.objects.filter(bot_id = attrs['bot']).exists():
            raise serializers.ValidationError({'bot':'Bot ID is not valid'})
        
        
        attrs['bot'] = Bot.objects.get(bot_id= attrs['bot'])
        if Order.objects.filter(order_number = attrs['order_number'],bot = attrs['bot']).exists():
            raise serializers.ValidationError({'order_number':'order number already exist'})
        for product in attrs['items']:
            if not Product.objects.filter(product_id = product).exists():
                raise serializers.ValidationError({'items':'product id is not valid'})
        # for product in attrs['items']:
        #     if not Product.objects.filter(product_id = product['product_id']).exists():
        #         raise serializers.ValidationError({'product_id':'product id is not valid'})

            
        return super().validate(attrs)
    


    def get_order_items(self, obj):
        
        return ', '.join([item.product.product_name for item in obj.order_items.all()])
        
    def create(self, validated_data):
        items = validated_data.pop('items')

        order = Order.objects.create(**validated_data)
        for item in items:
            product = Product.objects.get(product_id =item.product_id)
            OrderItem.objects.create(product = product,order=order)
        
        return order
        

class ProductCsvUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    bot_id = serializers.CharField()

    def validate(self, attrs):
      
        if not attrs['file'].name.endswith('.csv'):
            raise serializers.ValidationError({'file':"Only CSV files are allowed."})
        
        
        
        file = attrs['file']
        file.seek(0)



       

        df = pd.read_csv(attrs['file'])
        if 'Variant SKU' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Variant SKU column."})
        if 'Vendor' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Vendor column."})
        if 'Title' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Title column."})
        if 'Variant Price' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Variant Price column."})
        if 'Image Src' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Image Src column."})
        if 'Product Category' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Product Category column."})
        if 'Type' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain type column."})
        if 'Body (HTML)' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Body (HTML) column."})
        if 'Option1 Name' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option1 Name column."})
        if 'Option1 Value' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option1 Value column."})
        if 'Option2 Name' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option2 Name column."})
        if 'Option2 Value' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option2 Value column."})
        if 'Option3 Name' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option3 Name column."})
        if 'Option3 Value' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option3 Value column."})
        
        # empty_column = df.columns[df.isnull().any()].tolist()
        
        
        # if len(empty_column):
        #     raise serializers.ValidationError({'file':' ,'.join(empty_column)+" contain null please fill all."})
            
        return attrs
    


class BotProductCsvUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    bot_id = serializers.CharField()

    def validate(self, attrs):
      
        if not attrs['file'].name.endswith('.csv'):
            raise serializers.ValidationError({'file':"Only CSV files are allowed."})
        
        if not Bot.objects.filter(bot_id =attrs['bot_id']).exists():
            raise serializers.ValidationError({'bot':"Bot with the given bot_id does not exist"})
        
        file = attrs['file']
        file.seek(0)



       

        df = pd.read_csv(attrs['file'])
        if 'Variant SKU' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Variant SKU column."})
        if 'Vendor' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Vendor column."})
        if 'Title' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Title column."})
        if 'Variant Price' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Variant Price column."})
        if 'Image Src' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Image Src column."})
        if 'Product Category' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Product Category column."})
        if 'Type' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain type column."})
        if 'Body (HTML)' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Body (HTML) column."})
        if 'Option1 Name' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option1 Name column."})
        if 'Option1 Value' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option1 Value column."})
        if 'Option2 Name' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option2 Name column."})
        if 'Option2 Value' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option2 Value column."})
        if 'Option3 Name' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option3 Name column."})
        if 'Option3 Value' not in df.columns:
            raise serializers.ValidationError({'file':"file must contain Option3 Value column."})
        
        # empty_column = df.columns[df.isnull().any()].tolist()
        
        
        # if len(empty_column):
        #     raise serializers.ValidationError({'file':' ,'.join(empty_column)+" contain null please fill all."})
            
        return attrs
    

class PDFUserDetailSerializer(serializers.Serializer):
     id = serializers.IntegerField()
     web_username = serializers.CharField()
     web_password = serializers.CharField()
    #  order_id = serializers.CharField()
    #  order_date = serializers.DateField()
     total_earnings = serializers.CharField()
     total_users = serializers.IntegerField()
     first_name = serializers.CharField()
     last_name = serializers.CharField()
     email = serializers.EmailField()