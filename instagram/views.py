from django.shortcuts import render
from .serializers import CaptionSerializer,NewPostSerializer,PostSerialzer,InstagramUserDetailSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import InstagramPost
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



CONFIG = dotenv_values(".env")

KEY = CONFIG['key']
user = CONFIG['user']
passs = CONFIG['pasword']
limit = CONFIG['limit']
image_path = CONFIG['image_path']
# caption = CONFIG['caption']


class IsInstagramOrSuperUser(BasePermission):
   
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        group = request.user.groups.first() 
        if (group and group.name == "instagram") or request.user.is_superuser:
            return True
        else:
            return False
        
class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        group = request.user.groups.first() 
        if request.user.is_superuser:
            return True
        else:
            return False

# Function to interact with ChatGPT
def askGPT(message):
    openai.api_key = str(KEY)  # Add your OpenAI API key here
    messages = [
        {"role": "system", "content": "You are an intelligent assistant."},
        {"role": "user", "content": message},
    ]
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    reply = chat.choices[0].message['content']
    print("qq",reply)
    return reply

# Function to generate captions
def generate_captions(description):
    question = f"Generate 3 Instagram captions around {limit} words for the following description: {description}"
    response = askGPT(question)
    captions = response.split('\n')
    return [caption.strip() for caption in captions if caption.strip()]



class GenerateCaption(APIView):
    permission_classes = [IsAuthenticated,IsInstagramOrSuperUser]
    def post(self,request):
        
        serializer = CaptionSerializer(data = request.data)

        if serializer.is_valid():
            # Generate 3 best captions using ChatGPT
            # best_captions = generate_captions(serializer.validated_data['caption'])
            
            
            # clean_captions = []
            # for caption in best_captions:
            #     # Remove numbering and any extra quotes around the text
            #     clean_caption = caption.replace("1.", "").replace("2.", "").replace("3.", "").strip('"\'').strip('"').strip("'")

            #     clean_captions.append(clean_caption)

            clean_captions = ['Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae perferendis assumenda officiis facilis sit aperiam amet deleniti tenetur earum, a nemo illum repellendus, nostrum hic reprehenderit, perspiciatis vel! Minus eum ad laudantium numquam atque consequuntur asperiores aliquam mollitia ullam? Numquam fuga quam illum at, delectus laboriosam nisi. Tenetur, fuga error!','Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae perferendis assumenda officiis facilis sit aperiam amet deleniti tenetur earum, a nemo illum repellendus, nostrum hic reprehenderit, perspiciatis vel! Minus eum ad laudantium numquam atque consequuntur asperiores aliquam mollitia ullam? Numquam fuga quam illum at, delectus laboriosam nisi. Tenetur, fuga error!','Lorem ipsum dolor sit amet, consectetur adipisicing elit. Vitae perferendis assumenda officiis facilis sit aperiam amet deleniti tenetur earum, a nemo illum repellendus, nostrum hic reprehenderit, perspiciatis vel! Minus eum ad laudantium numquam atque consequuntur asperiores aliquam mollitia ullam? Numquam fuga quam illum at, delectus laboriosam nisi. Tenetur, fuga error!']

            
            return Response({'captions':clean_captions})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class MakePost(APIView):
    permission_classes = [IsAuthenticated,IsInstagramOrSuperUser]
    def post(self, request):
        post_serializer = NewPostSerializer(data=request.data)
        
        if post_serializer.is_valid():
            data = post_serializer.validated_data
            image_file = request.FILES.get('file')
            

            if 'two_factor_identifier' in data:
                
                
                try:
                    cl = Client()
                    user = cl.two_factor_login(data['username'], data['password'], data['two_factor_identifier'], data['verification_code'])
                    
                    
                # except (LoginRequired, ChallengeRequired, TwoFactorRequired) as e:
                #     return Response({'password': 'Instagram login failed due to authentication issues'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
            
                try:
                    cl = Client()
                    user = cl.login(data['username'], data['password'])
                    return Response({'message': 'Successfully posted on Instagram'}, status=status.HTTP_200_OK)
                    
                # except (LoginRequired, ChallengeRequired, TwoFactorRequired) as e:
                #     return Response({'password': 'Instagram login failed due to authentication issues'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    if 'challenge_required' in str(e):
                    # Store the 2FA info temporarily (you may store it in the session or a cache)
                        two_factor_info = cl.two_factor_auth_required(data['username'])
                        return Response({"message": "2FA required", "two_factor_identifier": two_factor_info['two_factor_identifier']}, status=status.HTTP_202_ACCEPTED)
                    return Response({'password': 'Instagram login failed due to authentication issues'}, status=status.HTTP_400_BAD_REQUEST)

           
            if image_file:
                try:
                    
                    unique_filename = f'{uuid.uuid4()}{os.path.splitext(image_file.name)[1]}'

                    
                    with open(unique_filename, 'wb+') as temp_image:
                        for chunk in image_file.chunks():
                            temp_image.write(chunk)

                    # Upload photo with caption to Instagram
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
    permission_classes = [IsAuthenticated,IsInstagramOrSuperUser]
    http_method_names = ['get']
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
        queryset = InstagramPost.objects.filter()
        # return queryset
        
        if self.request.user.is_superuser:
            
            user_id = self.request.query_params.get('user_id')
            if user_id:
                filter_conditions['user'] = user_id
                return queryset.filter(**filter_conditions)
            
            else:
                
                return queryset.filter(**filter_conditions)
        else:
            
            user_id = self.request.user
            filter_conditions['user'] = user_id
            return queryset.filter(**filter_conditions)
        
class InstagramUser(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
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
        ).values("id", "web_username", "total_post", "web_password")

        
        
        
        serializer = InstagramUserDetailSerializer(users,many=True)
        

        return Response(serializer.data)
