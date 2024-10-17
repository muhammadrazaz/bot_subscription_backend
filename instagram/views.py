from django.shortcuts import render
from .serializers import CaptionSerializer,NewPostSerializer,PostSerialzer,InstagramUserDetailSerializer,ConnectInstagramSerializer,CaptionPromptSerializer,InstagramPostWaitListSerializer,UpdatePostWaitSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import InstagramPost,InstagramSession,ChatGPTPrompt,InstagraPostWaitList,PostWithProblem
import openai
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired
from dotenv import dotenv_values
import os ,uuid
from datetime import datetime
from rest_framework.permissions import BasePermission
from  rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Count,Subquery,OuterRef,F,IntegerField,Value
from django.db.models.functions import Coalesce
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from instagrapi.mixins.challenge import ChallengeChoice
import time
import redis
from functools import partial
from io import BytesIO
import requests
import urllib.parse
from instagrapi.exceptions import ChallengeRequired
from auth_app.permissions import IsInGroupsOrSuperUser
import re
from rest_framework import generics
import pytz
from django.utils import timezone
from datetime import timedelta
from celery import shared_task

from bot_subscription_backend.celery import app

r = redis.StrictRedis(host='localhost', port=6379, db=0)

import logging

# # Set up basic configuration for logging
# logging.basicConfig(
#     level=logging.warning,  # You can also set this to INFO or WARNING
#     format='%(asctime)s %(levelname)s %(message)s',
#     handlers=[
#         # logging.FileHandler("/root/bot_subscription_backend/asgi.log"),
#         logging.StreamHandler()  # To also output logs to console
#     ]
# )

CONFIG = dotenv_values(".env")

KEY = CONFIG['key']
user = CONFIG['user']
passs = CONFIG['pasword']
limit = CONFIG['limit']
image_path = CONFIG['image_path']



# Proxy credentials
username = urllib.parse.quote(CONFIG['proxy_username'])
password = urllib.parse.quote(CONFIG['proxt_password'])  #
proxy_host = 'pr.oxylabs.io'
proxy_port = 7777




def get_code(user):
    print('get code function')
    # logging.warning('git code function is called')
    channel_layer = get_channel_layer()
    group_name = 'user_group_'+str(user.id)
    
    async_to_sync(channel_layer.group_send)(
    group_name,
    {
        'type': 'send_message',
        'message': 'otp required'
    }
    )

    # Wait for the OTP to be received and stored in Redis
    otp_key = 'otp_' + 'user_group_'+ str(user.id)
    otp = None
    max_wait_time = 120  # Maximum time to wait for OTP (in seconds)
    wait_interval = 5    # Interval to check for OTP (in seconds)
    waited_time = 0

    while not otp and waited_time < max_wait_time:
        otp = r.get(otp_key)
        if otp:
            # Decode from bytes to string
            otp = otp.decode('utf-8')
            print(f"OTP retrieved: {otp}")
            break
        time.sleep(wait_interval)
        waited_time += wait_interval



    if not otp:
        print("Failed to receive OTP within the time limit.")
        return False
    print(otp,'otp recived')
    return otp

def challenge_code_handler(username, choice,user):
    print('tet')
    # logging.warning('challage function is called')
    
    
    # if choice == ChallengeChoice.EMAIL:
    return get_code(user)
    return False







def set_proxies_according_to_region(country_code,city_name):
    # Create the proxy URL with the detected country code embedded in the username
    proxy_url_with_country = f"http://{username}-country-{country_code}-city-{city_name}:{password}@{proxy_host}:{proxy_port}"
    
    proxies = {
        'http': proxy_url_with_country,
        'https': proxy_url_with_country
    }
    
    print(f"Proxies set to target {country_code}.")
    return proxies


class ConnectInstgramAPIView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    def post(self,request):
        connect_serializer = ConnectInstagramSerializer(data = request.data)

        if connect_serializer.is_valid():
            data = connect_serializer.validated_data
            try:
                
                location = {'latitude':data['latitude'],'longitude':data['longitude']}
                country_code = data['country_code'].replace(' ','_')
                city_name = data['city_name'].replace(' ','_')
                print(country_code)
                # Set the proxy with the current location
                # logging.warning(country_code)
                # logging.warning(city_name)
                proxies_with_location = set_proxies_according_to_region(country_code,city_name)

    
                cl = Client()
                cl.challenge_code_handler = partial(challenge_code_handler, user=request.user)
                proxy = proxies_with_location['http']
                cl.set_proxy(proxy)
                user = cl.login(data['username'], data['password'])

                session_data = cl.get_settings()

                # Check if the session for the username already exists
                session, created = InstagramSession.objects.update_or_create(
                    user=request.user,
                    defaults={'session_data': session_data,'proxy':proxy}
                )
                
            except Exception as e:
                print(e)
                # logging.warning(e)
                return Response({'password': 'Instagram login failed due to authentication issues'+str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message':'success'},status=status.HTTP_201_CREATED)
        return Response(connect_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    def get(self,request):
        prompt = ChatGPTPrompt.objects.filter(user = request.user).first()
        if prompt:
            prompt = prompt.prompt
        else:
            prompt = ''
        try:
            try:
                session = InstagramSession.objects.get(user=request.user)
                session_data = session.session_data
                proxy = session.proxy
            except Exception as e:
                return Response({'username':'','prompt':prompt},status=status.HTTP_200_OK)  

           
            cl = Client()
          
            cl.set_proxy(proxy)
            cl.set_settings(session_data)
            

       
            account_info = cl.account_info()
            username = account_info.username
            return Response({'username':username,'prompt':prompt},status=status.HTTP_200_OK)  

     
        except Exception as e:
            # InstagramSession.objects.get(user=request.user).delete()
            print(f"Session not found for user: {request.user}")
            return Response({'username':'','prompt':prompt},status=status.HTTP_200_OK)  
        

class SetUpPromptAPIView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]

    def post(self,request):
        prompt_serializer = CaptionPromptSerializer(data = request.data)

        if prompt_serializer.is_valid():
            data = prompt_serializer.validated_data
            update,create = ChatGPTPrompt.objects.update_or_create(
                user = request.user,
                defaults={'prompt':data['prompt']}
            )
            return Response({'prompt':data['prompt']},status=status.HTTP_201_CREATED)
        return Response(prompt_serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# Function to interact with ChatGPT
def askGPT(message,prompt,image_file):
    import base64
    openai.api_key = str(KEY)  # Add your OpenAI API key here
    img_data = base64.b64encode(image_file.read()).decode('utf-8')
    messages = [
        {"role": "system", "content": prompt},
        {
      "role": "user",
      "content": [
        {"type": "text", "text": message},
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{img_data}",
          },
        },
      ],
    }
    ]
    chat = openai.ChatCompletion.create(  # Use `openai.Image.create` to handle images
        model="gpt-4o-mini",  # Use the GPT-4 model that supports image inputs
        messages=messages,  # Include the message you want
        # image=BytesIO(img_data)  # Pass the binary image data
    )
    
    reply = chat.choices[0].message['content']
    
    return reply

# Function to generate captions
def generate_captions(propmpt,image_file):
    question = f"Generate 3 Instagram captions around {limit} words for the following img"
    response = askGPT(question,propmpt,image_file)
    print(response)
    # captions = response.split('\n')
    # return [caption.strip() for caption in captions if caption.strip()]

    captions = re.split(r'(?<=\d\.)\s*', response)

    # Clean up the resulting list
    captions = [caption.strip(' "') for caption in captions if caption]
    return captions[1:]



class GenerateCaption(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    def post(self,request):
        
        serializer = CaptionSerializer(data = request.data)

        if serializer.is_valid():
            # Generate 3 best captions using ChatGPT
            image_file = request.FILES['file']
            prompt = ChatGPTPrompt.objects.get(user=request.user).prompt
            best_captions = generate_captions(prompt,image_file)
            
            
            clean_captions = []
            for caption in best_captions:
                # Remove numbering and any extra quotes around the text
                clean_caption = caption.replace("1.", "").replace("2.", "").replace("3.", "").strip('"\'').strip('"').strip("'")

                clean_captions.append(clean_caption)

            # clean_captions = ['Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae perferendis assumenda officiis facilis sit aperiam amet deleniti tenetur earum, a nemo illum repellendus, nostrum hic reprehenderit, perspiciatis vel! Minus eum ad laudantium numquam atque consequuntur asperiores aliquam mollitia ullam? Numquam fuga quam illum at, delectus laboriosam nisi. Tenetur, fuga error!','Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae perferendis assumenda officiis facilis sit aperiam amet deleniti tenetur earum, a nemo illum repellendus, nostrum hic reprehenderit, perspiciatis vel! Minus eum ad laudantium numquam atque consequuntur asperiores aliquam mollitia ullam? Numquam fuga quam illum at, delectus laboriosam nisi. Tenetur, fuga error!','Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae perferendis assumenda officiis facilis sit aperiam amet deleniti tenetur earum, a nemo illum repellendus, nostrum hic reprehenderit, perspiciatis vel! Minus eum ad laudantium numquam atque consequuntur asperiores aliquam mollitia ullam? Numquam fuga quam illum at, delectus laboriosam nisi. Tenetur, fuga error!']

            
            return Response({'captions':clean_captions})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    








class MakePost(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    def post(self, request):
        post_serializer = NewPostSerializer(data=request.data)
       
        
        if post_serializer.is_valid():
        
            image_file = request.FILES.get('file')
            data = post_serializer.validated_data
        
   
            
            try:

                session = InstagramSession.objects.get(user=request.user)
                session_data = session.session_data

            
                cl = Client()
                cl.set_proxy(session.proxy)
                cl.set_settings(session_data)
                
            except Exception as e:
                print(e)
                
                return Response({'password': 'Instagram login failed due to authentication issues'}, status=status.HTTP_400_BAD_REQUEST)

           
            if image_file:
                try:
                    
                    unique_filename = f'{uuid.uuid4()}{os.path.splitext(image_file.name)[1]}'

                    
                    with open(unique_filename, 'wb+') as temp_image:
                        for chunk in image_file.chunks():
                            temp_image.write(chunk)

                   
                    media = cl.photo_upload(unique_filename, data['caption'])

                    
                    

                    
                    post_url = f'https://www.instagram.com/p/{media.code}/'
                    
                    InstagramPost.objects.create(user = self.request.user,file=image_file,post_url = post_url)
                    os.remove(unique_filename)

                    return Response({'message': 'Successfully posted on Instagram'}, status=status.HTTP_200_OK)

                except Exception as e:
                    return Response({'error': f'Failed to upload the image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerialzer
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    http_method_names = ['get']
    def get_queryset(self):
        dates = self.request.GET.getlist('dates[]')
        filter_conditions = {}
        if dates:
            start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            filter_conditions = {
            'date_time__gt': start_date,
            'date_time__lt': end_date,
            }
        queryset = InstagramPost.objects.filter()
        # return queryset
        
        if self.request.user.is_superuser:
            
            user_id = self.request.query_params.get('user_id')
            if user_id:
                filter_conditions['user'] = user_id
            #     return queryset.filter(**filter_conditions)
            
            # else:
                
            #     return queryset.filter(**filter_conditions)
        else:
            
            user_id = self.request.user
            filter_conditions['user'] = user_id
        return queryset.filter(**filter_conditions).order_by('-date_time')
    

class DisconnectInstagramApiView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    def get(self,request):
        try:
                session = InstagramSession.objects.get(user=request.user)
                session_data = session.session_data
                cl = Client()
                cl.set_proxy(session.proxy)
                cl.set_settings(session_data)
                # account_info = cl.account_info()
                cl.logout()
                InstagramSession.objects.filter(user=request.user).first().delete()
                
        except Exception as e:
            InstagramSession.objects.filter(user=request.user).first().delete()
            print(e)
           
        return Response({'message':'success'},status=status.HTTP_200_OK) 
        
class InstagramUser(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =["VA"])]
    def get(self, request):
        
        users = User.objects.filter(groups__name='instagram').annotate(
    total_post=Coalesce(
        Subquery(
            InstagramPost.objects.filter(user=OuterRef('id')).values('user_id').annotate(
                total_sum=Count('user_id')
            ).values('total_sum')[:1]
        ),
        Value(0)
            ),
        ).annotate(
            user_id=F('id'),
            web_username=F('username'),
            web_password=F('password')
        ).values("id", "web_username", "total_post", "web_password","first_name",'last_name',"email")

        
        
        
        serializer = InstagramUserDetailSerializer(users,many=True)
        

        return Response(serializer.data)
    

class GetPostWaitList(generics.GenericAPIView):
    serializer_class = InstagramPostWaitListSerializer
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    def get(self,request):
        time_zone = request.query_params.get('timezone')
        
        user_tz = pytz.timezone(time_zone)

        
        user_time = timezone.now().astimezone(user_tz)
     
        utc_time = user_time.astimezone(pytz.utc)




        minutes = user_time.minute

        # If the minutes are between 0 and 30, round up to 30
        # if minutes < 30:
        #     nearest_time = user_time.replace(minute=30, second=0, microsecond=0)
        # # If the minutes are greater than or equal to 30, round to the next hour
        # else:
        # nearest_time = (user_time + timedelta(hours=1)).replace(minute=0, second=0,)

        

        utc_time = user_time.astimezone(pytz.utc)
        # posts = InstagraPostWaitList.objects.filter(date_time__gte = utc_time)
        posts = InstagraPostWaitList.objects.filter(date_time__gt = utc_time,user = request.user)


        post_data = []
        for post in posts:
            
      
            

            local_time = post.date_time.astimezone(user_tz)
            # nearest_time = local_time + timedelta(hours=4)
            post_data.append(  {
                    'id' : post.pk,
                    'date_time':local_time,
                    'caption':post.caption,
                    'img' : post.file.url,
                    })
        if len(post_data):
        
            utc_time = post_data[-1]['date_time']


        for i in range(len(post_data),28):
            utc_time  = utc_time + timedelta(hours=4)
            post_detail  =  {
            'id' :'',
            'date_time':utc_time,
            'caption':'',
            'img' : '',
            }
            post_data.append(post_detail)
            
            

        # serializer_data = self.get_serializer(data = post_data,many=True)
    

        return Response({"data":post_data},status=status.HTTP_200_OK)
    
    def post(self,request):
        wait_list_serializer = self.get_serializer(data = request.data)

        if wait_list_serializer.is_valid():
            data = wait_list_serializer.validated_data
            image_file = request.FILES.get('file')


            time_zone = data['time_zone']
            user_tz = pytz.timezone(time_zone)
            user_time = timezone.now().astimezone(user_tz)
            utc_time = user_time.astimezone(pytz.utc)
           

            post = InstagraPostWaitList.objects.filter(date_time__gte = utc_time,user=request.user).order_by('-date_time').first()

            if post:
                new_post_time = post.date_time + timedelta(hours=4)
            else:


                # minutes = utc_time.minute

                # # If the minutes are between 0 and 30, round up to 30
                # if minutes < 30:
                #     nearest_time = utc_time.replace(minute=30, second=0, microsecond=0)
                # # If the minutes are greater than or equal to 30, round to the next hour
                # else:
                #     nearest_time = (utc_time + timedelta(hours=1)).replace(minute=0, second=0,)
                # nearest_time = (user_time + timedelta(hours=1)).replace(minute=0, second=0,)
                new_post_time = (user_time + timedelta(hours=4))

            new_post = InstagraPostWaitList.objects.create(user=request.user,caption = data['caption'],file = image_file,date_time = new_post_time,time_zone = time_zone)

            # delay = (utc_time - new_post_time).total_seconds()
            delay = (new_post_time - utc_time).total_seconds()
            

            # Schedule the task to run at the specified time
            task_id = post_to_instagram.apply_async((new_post.id,), countdown=delay)
            new_post.task_id =task_id
            new_post.save()
            # return 

            return Response({'message' : 'success'},status=status.HTTP_201_CREATED)
        
        return Response(wait_list_serializer.errors,status=status.HTTP_400_BAD_REQUEST)




class UpdateWaitPost(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['instagram'])]
    def delete(self, request, pk, format=None):
        try:
            instance = InstagraPostWaitList.objects.get(pk=pk)
            # Revoke the existing task
            if instance.task_id:
                app.control.revoke(instance.task_id, terminate=True)  


            other_posts = InstagraPostWaitList.objects.filter(user=request.user,date_time__gt = instance.date_time)
            instance.delete()

            # Update the date_time of other posts
            for post in other_posts:
                post.date_time -= timedelta(hours=4)
                post.save()  

                if post.task_id:
                    app.control.revoke(post.task_id, terminate=True)  

                
                utc_time = datetime.now().astimezone(pytz.UTC)
                post_time = post.date_time.astimezone(pytz.UTC)
                delay = ( post_time - utc_time ).total_seconds()
                print(delay,post_time,utc_time)

                # Reschedule the task and store the new task ID
                task = post_to_instagram.apply_async((post.id,), countdown=delay)
                post.task_id = task.id
                post.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except InstagraPostWaitList.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, pk, format=None):
        try:
            # Get the instance of the object to be updated
            instance = InstagraPostWaitList.objects.get(pk=pk)
            serializer = UpdatePostWaitSerializer(data = request.data)
            if serializer.is_valid():
       
                instance.caption = serializer.validated_data['caption']
                instance.save()
                return Response({'message' : 'success'}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except InstagraPostWaitList.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)
        
       

@shared_task
def post_to_instagram(post_id):
    print('task_id',post_id)
    try:
        post = InstagraPostWaitList.objects.get(id=post_id)
        user_id = post.user
        
        try:
            session = InstagramSession.objects.get(user=user_id)
            session_data = session.session_data
            proxy = session.proxy
        except Exception as e:
            PostWithProblem.objects.create(data = post,error = str(e))
            post.delete()
            print(str(e))
            return

        try:  
            
            cl = Client()
            cl.set_proxy(proxy)
            cl.set_settings(session_data)
        except Exception as e:
            PostWithProblem.objects.create(data = post,error = str(e))
            post.delete()
            print(str(e))
            return

        try:
            from django.conf import settings
                    
            image_file = post.file  # This is an ImageFieldFile object

            # Access the actual file path as a string
            image_path = os.path.join(settings.MEDIA_ROOT,'instagram_imgs' ,os.path.basename(image_file.name))

            
            media = cl.photo_upload(image_path, post.caption)

            
            

            
            post_url = f'https://www.instagram.com/p/{media.code}/'
            
            InstagramPost.objects.create(user = user_id,caption =post.caption,file=post.file,post_url = post_url)
            # os.remove(unique_filename)

            

        except Exception as e:
            PostWithProblem.objects.create(data = post,error = str(e))
            post.delete()
            print(e,'1')
            return

        post.delete()
        print(f"Posted to Instagram for user {post.user}")
    except InstagraPostWaitList.DoesNotExist:
        print("Post not found")
        
      
        

