# yourapp/middleware.py
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        # Fetch the user using the user_id
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        return user
    except Exception:
        return None


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        
        query_string = scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
       
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()
        
        if isinstance(scope['user'], AnonymousUser) or scope['user'] is None:
            raise DenyConnection("Authentication failed")
        
        return await super().__call__(scope, receive, send)
