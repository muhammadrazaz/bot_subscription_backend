# your_app_name/consumers.py

import json
from channels.consumer import SyncConsumer,AsyncConsumer
import redis

# Setup Redis connection (assuming Redis is running on localhost and port 6379)
r = redis.StrictRedis(host='localhost', port=6379, db=0)
# class MySyncConsumer(SyncConsumer):
#     def websocket_connect(self,event):
#         print('connected',event)
#         self.send({
#             'type' :'websocket.accept'
#         })
#     def websocket_receive(self,event):
#         print('received',event)
    
#     def websocket_disconnect(self,event):
#         print('connected',event)


class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        
        user = self.scope['user']
        self.group_name = "user_group_"+str(user.id)
        r.delete('otp_' + self.group_name)
        print(r.get('user_group_'+str(user.id)))
        print(self.group_name,'outsite')
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name  # This is the unique channel name for the WebSocket
        )
        await self.send({
            'type' :'websocket.accept',
        })

    async def websocket_receive(self,event):
        print('received',event)
        otp_received = event.get('text', None)
        
        if otp_received.isdigit():
            r.set('otp_' + self.group_name, otp_received)
            await self.send({
                'type' :'websocket.send',
                'text' : 'otp received'
            })
        await self.send({
                'type' :'websocket.send',
                'text' : 'message received'
            })

    async def send_message(self, event):
        message = event['message']
        print('test')
        await self.send({
            'type' :'websocket.send',
            'text' : message
        })

    
    async def websocket_disconnect(self,event):
        # await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print('dis',event)

        # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        print('tse')
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))



    
