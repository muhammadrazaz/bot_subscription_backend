from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import SubscriptionSerializer,UserDetailSerializer,ClientDetailSerializer,CsvUploadSerializer
from .models import Subscription
from  rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from django.db.models import Sum,Count,Case,When,IntegerField,F, Value, CharField,Subquery,OuterRef
from django.db.models.functions import Cast, Coalesce
from rest_framework.response import Response
from auth_app.models import Bot
from datetime import datetime
from django.db.models.functions import ExtractMonth, ExtractYear
import calendar
from django.contrib.auth.models import User,Group
import csv
from rest_framework import status
import pandas as pd
from rest_framework.permissions import BasePermission
from io import StringIO
from rest_framework.exceptions import NotFound

class IsSubsriptionOrSuperUser(BasePermission):
   

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        group = request.user.groups.first() 
        if (group and group.name == "subscription") or request.user.is_superuser:
            return True
        else:
            return False
        
class IsSuperUser(BasePermission):
   

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        else:
            return False

    

    
class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated,IsSubsriptionOrSuperUser]
    def get(self, request):
        dates = request.GET.getlist('dates[]')
        start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        filter_conditions = {
        'start_date__gt': start_date,
        'start_date__lt': end_date,
    }

    # Conditionally add bot filter if bot is not -1
        
        if not request.user.is_superuser:
            bot = Bot.objects.get(user=request.user)
            filter_conditions['bot'] = bot

        
            
        sub_data = Subscription.objects.filter(**filter_conditions).aggregate(
            earnings =Coalesce(Sum('price'), 0),
            new_sub = Coalesce(Count('id'),0),
            active=Sum(Case(When(cancelled=False, then=1), output_field=IntegerField())),
            expire=Sum(Case(When(cancelled=True, then=1), output_field=IntegerField()))
                )
        plan_counts = Subscription.objects.filter(**filter_conditions).values('plan').annotate(value=Count('plan')).values(name=F('plan'), value=F('value')).order_by('name')[:3]
        
    
        overall_earnings = Subscription.objects.filter(**filter_conditions).aggregate(all_earnings =Coalesce(Sum('price'),0) )
        
        month_names = {i: calendar.month_abbr[i] for i in range(1, 13)}
        
        filter_conditions = {
        'year': start_date.year,
        }


        
        if not request.user.is_superuser:
            bot = Bot.objects.get(user=request.user)
            filter_conditions['bot'] = bot
        
        monthly_earnings = Subscription.objects.annotate(
            month=ExtractMonth('start_date'),
            year=ExtractYear('start_date')
        ).filter(**filter_conditions)\
        .values('month') \
        .annotate(total_earnings=Sum('price')) \
        .order_by('month')

        
        earnings_by_month = {i: 0 for i in range(1, 13)}

        
        for earnings in monthly_earnings:
            month_number = earnings['month']
            earnings_by_month[month_number] = earnings['total_earnings']


        

        monthly_earnings = []
        for month_number in range(1, 13):
            month_name = month_names[month_number]
            total = earnings_by_month[month_number]
            monthly_earnings.append({"name":month_name,'sale':total})
          

        month_abbr = {i: calendar.month_abbr[i] for i in range(1, 13)}

        
        monthly_payment_earnings = Subscription.objects.annotate(
            month=ExtractMonth('start_date'),
            year=ExtractYear('start_date')
        ).filter(**filter_conditions)\
        .values('month', 'payment') \
        .annotate(total_earnings=Sum('price')) \
        .order_by('month', 'payment')

        
        earnings_by_month_payment = {
            (month, payment): 0 for month in range(1, 13) for payment in ['paypal', 'stripe', 'cryptocurrency']
        }

        
        for earnings in monthly_payment_earnings:
            month_number = earnings['month']
            payment = earnings['payment']
            earnings_by_month_payment[(month_number, payment)] = earnings['total_earnings']

        monthly_payment_sale = []
        for month_number in range(1, 13):
            month_name = month_abbr[month_number]
            pay_detail = {"name":month_name}
            for payment in ['paypal', 'stripe', 'cryptocurrency']:
                total = earnings_by_month_payment[(month_number, payment)]
                
                
                pay_detail[payment] = total
            monthly_payment_sale.append(pay_detail)

            # Get the group instance
            group = Group.objects.get(name="subscription")

            # Count users in the group
            user_count = User.objects.filter(groups=group).count()

    
        response_data = {
            'earnings' : sub_data['earnings'],
            'new_subscriptions' : sub_data['new_sub'],
            'overall_earnings' : overall_earnings['all_earnings'],
            'user_status':[{'name':'expire','value':sub_data['expire'] if sub_data['expire'] else 0},{'name':'active','value':sub_data['active'] if sub_data['active'] else 0}],
            'plan' : plan_counts,
            'monthly_earnings':monthly_earnings,
            'payment_earning' : monthly_payment_sale,
            'total_users' : User.objects.filter(groups=group).count() if request.user.is_superuser else -1

        }


        return Response(response_data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    http_method_names = ('get', 'post')
    permission_classes = [IsAuthenticated,IsSubsriptionOrSuperUser]
    
   
    def get_queryset(self):
        dates = self.request.GET.getlist('dates[]')
        filter_conditions = {}
        if dates:
            start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            filter_conditions = {
            'start_date__gt': start_date,
            'start_date__lt': end_date,
            }
        queryset = Subscription.objects.annotate(
            cancelled_str=Case(
                When(cancelled=True, then=Value("True")),
                When(cancelled=False, then=Value("False")),
                output_field=CharField()
            ),
            status_str=Case(
                When(status=True, then=Value("True")),
                When(status=False, then=Value("False")),
                output_field=CharField()
            )
        )
        
        # Superuser-specific filtering
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            bot_id = self.request.query_params.get('bot_id')
            if user_id:
                bot_id = Bot.objects.get(user=user_id)
                filter_conditions['bot'] =bot_id
                return queryset.filter(**filter_conditions)
            # elif bot_id:
            #     bot_id = Bot.objects.get(bot=bot_id)
            #     filter_conditions['bot'] =bot_id
            #     return queryset.filter(**filter_conditions)
            else :
                
                return queryset.filter(**filter_conditions)
            return queryset
        
        # Regular user filtering based on bot
        bot_id = Bot.objects.get(user=self.request.user)
        filter_conditions['bot'] =bot_id
        return queryset.filter(**filter_conditions)
        
        
        
    



class UserApiView(APIView):
    permission_classes = [IsAuthenticated,IsSubsriptionOrSuperUser]
    def get(self, request):
        users = User.objects.filter(groups__name = 'subscription').annotate(
    bot_id=Subquery(
        Bot.objects.filter(user_id=OuterRef('id')).values('id')[:1]
    ),
    total_earnings=Subquery(
        Subscription.objects.filter(bot=OuterRef('bot_id')).values('user_id').annotate(
            total_sum=Sum('price')
        ).values('total_sum')[:1]
        ),
        total_users=Subquery(
            Subscription.objects.filter(bot=OuterRef('bot_id')).values('user_id').annotate(
                users=Count('id')
            ).values('users')[:1]
        )
        ).annotate(
        user_id=F('id'),
        web_username=F('username'),
        web_password = F('password')
        ).values("id", "web_username", "total_earnings", "total_users","web_password")

        
        
        
        serializer = UserDetailSerializer(users,many=True)
        

        return Response(serializer.data)
    
class ClientDetailViewSet(viewsets.ModelViewSet):
    serializer_class = ClientDetailSerializer
    permission_classes = [IsAuthenticated,IsSuperUser]
    

    def get_queryset(self):
        queryset = Bot.objects.all()
        
        
        user_id = self.request.query_params.get('user_id')
        obj = queryset.filter(user=user_id)
        
       
        
        return obj
    

class CsvUploadView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def post(self, request, *args, **kwargs):
        upload_serializer = CsvUploadSerializer(data=request.data)
        if upload_serializer.is_valid():
            file = upload_serializer.validated_data['file']
            file.seek(0)  # Reset file pointer to the beginning

            

            file = pd.read_csv(request.FILES['file'].file)
            
            
            for index,row in file.iterrows():
                bot_id = row.pop('bot_id')
                print(row)
                Bot.objects.update_or_create(bot_id = bot_id,defaults=row.to_dict())
                
            
                

            
            return Response({"message": "Data imported successfully."}, status=status.HTTP_200_OK)
        
        return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    






# ################################# admin view 


class BotSubscriberViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()

    def get_object(self):
        
        subscription_id = self.kwargs.get('pk')
        try:
            
            return Subscription.objects.get(subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            
            raise NotFound("Subscription with the given subscription_id does not exist")