from django.shortcuts import render
from .serializers import ProductSerializer,ProductCsvUploadSerializer,OrderSerializer,PDFUserDetailSerializer

from .models import Product,Order,OrderItem,ProductDetail
from auth_app.models import Bot
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission,IsAuthenticated
from django.contrib.auth.models import User,Group
from rest_framework.response import Response
from django.db.models import Subquery,OuterRef,Count,Sum,Value,DecimalField,When,Case,F,IntegerField
from django.db.models.functions import Coalesce, ExtractMonth,ExtractYear
import pandas as pd
from datetime import datetime
import calendar
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from bs4 import BeautifulSoup
from rest_framework.exceptions import NotFound

from auth_app.permissions import IsInGroupsOrSuperUser

# class IsProductOrSuperUser(BasePermission):
#     def has_permission(self, request, view):
#         # if not request.user or not request.user.is_authenticated:
#         #     return False
        
#         group = request.user.groups.first() 
#         if (group and group.name == "product") or request.user.is_superuser:
#             return True
#         else:
#             return False

class ProductDashboardView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['product','VA'])]
    def get(self,request):
        dates = request.GET.getlist('dates[]')
        start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        filter_conditions = {
        'order_date__gt': start_date,
        'order_date__lt': end_date,
        }
        
        if not request.user.is_superuser:
            bot = Bot.objects.get(user=request.user)
            filter_conditions['bot'] = bot


        dashboard_detail = Order.objects.filter(**filter_conditions).aggregate(
        earnings=Coalesce(Sum('order_total'),0,output_field=IntegerField()),
        new_order=Count('id'),
        completed=Coalesce(Sum(Case(When(status="completed", then=1), output_field=IntegerField())),0),
        pending=Coalesce(Sum(Case(When(status="pending", then=1), output_field=IntegerField(), default=0)),0)
        )
       
   
        status_summary = [
            {"name": "pending", "value": dashboard_detail['pending']},
            {"name": "completed", "value": dashboard_detail['completed']}
        ]

        
        dashboard_detail.update({
            'status_summary': status_summary
        })

        bot_filter_conditions = {
     
        }
        if not request.user.is_superuser:
            bot = Bot.objects.get(user=request.user)
            bot_filter_conditions['bot'] = bot

        dashboard_detail['total_products'] = Product.objects.filter(**bot_filter_conditions).count()


        overall_earnings = Order.objects.filter(**bot_filter_conditions).aggregate(overall_earnings=Coalesce(Sum('order_total'),0,output_field=IntegerField()))

        dashboard_detail['overall_earnings'] = overall_earnings['overall_earnings']

        monthly_earnings = [{"name":calendar.month_abbr[i],"sale": 0}  for i in range(1, 13)]


        filter_conditions = {
        'year': start_date.year,
        }

        if not request.user.is_superuser:
            bot = Bot.objects.get(user=request.user)
            filter_conditions['bot'] = bot


        earnings = (
        Order.objects
        .annotate(month=ExtractMonth('order_date'), year=ExtractYear('order_date'))
        .filter(**filter_conditions)
        .values('month')
        .annotate(total_earnings=Coalesce(Sum('order_total'), Value(0),output_field=DecimalField()))
        .order_by('month')
        )
        
        
        for earning in earnings:
            monthly_earnings[earning['month']-1]['sale'] = earning['total_earnings']

        results = Order.objects.annotate(
        month=ExtractMonth('order_date'),
        year=ExtractYear('order_date')
        ).filter(**filter_conditions).values('month').annotate(
        stripe=Sum(Case(
            When(payment='stripe', then=F('order_total')),
            default=0,
            output_field=DecimalField()
        )),
        paypal=Sum(Case(
            When(payment='paypal', then=F('order_total')),
            default=0,
            output_field=DecimalField()
        )),
        crypto=Sum(Case(
            When(payment='crypto', then=F('order_total')),
            default=0,
            output_field=DecimalField()
        ))
    ).order_by('month')

        monthly_payment_earnings = [{"name":calendar.month_abbr[i],"stripe": 0,'paypal':0,'crypto':0}  for i in range(1, 13)]
        for result in results:
   
            monthly_payment_earnings[result['month']-1]['stripe'] = result['stripe']
            monthly_payment_earnings[result['month']-1]['paypal'] = result['paypal']
            monthly_payment_earnings[result['month']-1]['crypto'] = result['crypto']
        

        dashboard_detail['payment_earnings'] = monthly_payment_earnings

        
        dashboard_detail['monthly_earnings'] = monthly_earnings

        category_counts = Product.objects.filter(**bot_filter_conditions).values(name =F('product_category')).annotate(value=Count('product_category'))[:3]
        dashboard_detail['category_counts'] = category_counts
        group = Group.objects.get(name="product")
        dashboard_detail['total_users'] =  User.objects.filter(groups=group).count() if request.user.is_superuser else -1
        
        return Response(dashboard_detail)
class ProductViewset(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes =[IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['product','VA'])]

    def get_queryset(self):
       
        if self.request.user.is_superuser or self.request.user.groups.filter(name ="VA"):
            bot_id = self.request.query_params.get('bot_id')
            # user_id = self.request.query_params.get('user_id')
            if bot_id:
                # bot  = Bot.objects.get(bot_id=bot_id)
                return Product.objects.filter(bot=bot_id)
            # if user_id:
            #     bot  = Bot.objects.get(user=user_id)
            #     return Product.objects.filter(bot=bot)
            else:
                return Product.objects.filter()
        else:
            bot = Bot.objects.get(user=self.request.user)
            return Product.objects.filter(bot=bot)
        
class OrderViewset(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['product','VA'])]

    def get_queryset(self):
        dates = self.request.GET.getlist('dates[]')
        filter_conditions = {}
        if dates:
            start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            filter_conditions = {
            'order_date__gt': start_date,
            'order_date__lt': end_date,
            }
        queryset = Order.objects.filter()
        # return queryset
        
        if self.request.user.is_superuser or self.request.user.groups.filter(name ="VA"):
            
            # user_id = self.request.query_params.get('user_id')
            bot_id = self.request.query_params.get('bot_id')
            print(bot_id)
            if bot_id:
                # bot = Bot.objects.get(user=user_id)
                filter_conditions['bot'] = bot_id
            #     return queryset.filter(**filter_conditions)
            # elif bot_id:
                 
            #      bot = Bot.objects.get(bot_id=bot_id)
                 
            #      return queryset.filter(bot=bot)
            # else:
                
            #     return queryset.filter(**filter_conditions)
        else:
            
            user_id = self.request.user
            bot = Bot.objects.get(user=user_id)
            filter_conditions['bot'] = bot
        return queryset.filter(**filter_conditions).order_by('-order_date')
        
def download_and_save_image(image_url, storage_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_name = storage_path.split('/')[-1]  # Extract the image name from the path
        image_content = ContentFile(response.content, name=image_name)
        
        # Save the image to the specified storage path
        file_path = default_storage.save(storage_path, image_content)
        return file_path
    return None

class ProductCsvUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        upload_serializer = ProductCsvUploadSerializer(data=request.data)
        if upload_serializer.is_valid():
            file = upload_serializer.validated_data['file']
            file.seek(0)  # Reset file pointer to the beginning

            

            file = pd.read_csv(upload_serializer.validated_data['file'])
            
            bot = Bot.objects.get(user=request.user)
            product = ''
            option1_name = ''
            option2_name = ''
            option3_name = ''
            product_detail =[]
            product_create = []
            for index,row in file.iterrows():
                
                if not pd.isna(row['Title']):
                    image_url = row['Image Src']
                    image_name = image_url.split('?')[0].split('/')[-1]
                    storage_path = f'products/imgs/{image_name}'
        
                   
                    file_path = download_and_save_image(row['Image Src'], storage_path)
                    
                    
                    product_update,product = Product.objects.update_or_create(bot=bot,product_id =row['Variant SKU'],defaults={'product_name':row['Title'],'price' :row['Variant Price'],'product_img' :file_path,'product_category' :row['Product Category'],'sub_category' :row['Type'],'description' :BeautifulSoup(row['Body (HTML)'],'html.parser').get_text() if not pd.isna(row['Body (HTML)']) else row['Body (HTML)'],'brand':row['Vendor']})
                    
                    if product:
                        if  not pd.isna(row['Option1 Name']):
                            option1_name =  row['Option1 Name']
                            product_detail.append(ProductDetail(product = product_update,option_name = option1_name,option_value=row['Option1 Name']))
                        if not pd.isna(row['Option2 Name']):
                            option2_name =  row['Option2 Name']
                            product_detail.append(ProductDetail(product = product_update,option_name = option2_name,option_value=row['Option2 Name']))
                        if not pd.isna(row['Option3 Name']):
                            option3_name =  row['Option3 Name']
                            product_detail.append(ProductDetail(product = product_update,option_name = option3_name,option_value=row['Option3 Name']))
                else:
                    if product:
                    
                        if not pd.isna(row['Option1 Value']):
                        
                            product_detail.append(ProductDetail(product = product_update,option_name = option1_name,option_value=row['Option1 Value']))
                            

                        if not pd.isna(row['Option2 Value']):
                            
                            product_detail.append(ProductDetail(product = product_update,option_name = option2_name,option_value=row['Option2 Value']))
                        

                        if not pd.isna(row['Option3 Value']):
                            
                            product_detail.append(ProductDetail(product = product_update,option_name = option3_name,option_value=row['Option3 Value']))
                        

            ProductDetail.objects.bulk_create(product_detail)
            
            return Response({"message": "Data imported successfully."}, status=status.HTTP_200_OK)
        
        return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    



class ProudctUserApiView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['VA'])]
    def get(self, request):
        users = Bot.objects.filter(type = 'product').annotate(
    # bot_id=Subquery(
    #     Bot.objects.filter(user_id=OuterRef('id')).values('id')[:1]
    # ),
    total_earnings=Subquery(
        Order.objects.filter(bot=OuterRef('bot_id')).values('bot_id').annotate(
            total_sum=Coalesce(Sum('order_total'),0,output_field=IntegerField())
        ).values('total_sum')[:1]
        ),
        total_users = Subquery(
    Order.objects.filter(bot=OuterRef('bot_id'))
    .values('bot')  # We just need a reference for grouping
    .annotate(total_users=Coalesce(Count('username', distinct=True),0,output_field=IntegerField()))
    .values('total_users')[:1]  # This ensures you're getting a single count
)
        ).annotate(
        web_username=F('user__username'),
        web_password = F('user__password'),
        first_name = F('user__first_name'),
        last_name = F('user__last_name'),
        email = F('user__email'),
        ).values("id", "web_username", "total_earnings", "total_users","web_password","first_name",'last_name',"email")

        # users['total_users'] = 0

        serializer = PDFUserDetailSerializer(users,many=True)
        

        return Response(serializer.data)
    


    # Admin View

class BotProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_object(self):
    
        product_id = self.kwargs.get('pk')
        try:
            
            return Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            
            raise NotFound("Subscription with the given subscription_id does not exist")
        
class BotOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_object(self):
    
        order_number = self.kwargs.get('pk')
        try:
            
            return Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            
            raise NotFound("Subscription with the given subscription_id does not exist")
        

class BotProductCsvUploadView(APIView):
    
    def post(self, request, *args, **kwargs):
        upload_serializer = ProductCsvUploadSerializer(data=request.data)
        if upload_serializer.is_valid():
            file = upload_serializer.validated_data['file']
            file.seek(0)  # Reset file pointer to the beginning

            

            file = pd.read_csv(upload_serializer.validated_data['file'])
            
            bot = upload_serializer.validated_data['bot_id']
            product = ''
            option1_name = ''
            option2_name = ''
            option3_name = ''
            product_detail =[]
            product_create = []
            for index,row in file.iterrows():
                
                if not pd.isna(row['Title']):
                    image_url = row['Image Src']
                    image_name = image_url.split('?')[0].split('/')[-1]
                    storage_path = f'products/imgs/{image_name}'
        
                   
                    file_path = download_and_save_image(row['Image Src'], storage_path)
                    
                    
                    product_update,product = Product.objects.update_or_create(bot=bot,product_id =row['Variant SKU'],defaults={'product_name':row['Title'],'price' :row['Variant Price'],'product_img' :file_path,'product_category' :row['Product Category'],'sub_category' :row['Type'],'description' :BeautifulSoup(row['Body (HTML)'],'html.parser').get_text() if not pd.isna(row['Body (HTML)']) else row['Body (HTML)'],'brand':row['Vendor']})
                    
                    if product:
                        if  not pd.isna(row['Option1 Name']):
                            option1_name =  row['Option1 Name']
                            product_detail.append(ProductDetail(product = product_update,option_name = option1_name,option_value=row['Option1 Name']))
                        if not pd.isna(row['Option2 Name']):
                            option2_name =  row['Option2 Name']
                            product_detail.append(ProductDetail(product = product_update,option_name = option2_name,option_value=row['Option2 Name']))
                        if not pd.isna(row['Option3 Name']):
                            option3_name =  row['Option3 Name']
                            product_detail.append(ProductDetail(product = product_update,option_name = option3_name,option_value=row['Option3 Name']))
                else:
                    if product:
                    
                        if not pd.isna(row['Option1 Value']):
                        
                            product_detail.append(ProductDetail(product = product_update,option_name = option1_name,option_value=row['Option1 Value']))
                            

                        if not pd.isna(row['Option2 Value']):
                            
                            product_detail.append(ProductDetail(product = product_update,option_name = option2_name,option_value=row['Option2 Value']))
                        

                        if not pd.isna(row['Option3 Value']):
                            
                            product_detail.append(ProductDetail(product = product_update,option_name = option3_name,option_value=row['Option3 Value']))
                        

            ProductDetail.objects.bulk_create(product_detail)
            
            return Response({"message": "Data imported successfully."}, status=status.HTTP_200_OK)
        
        return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)