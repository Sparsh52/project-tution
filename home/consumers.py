# import json
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.forms.models import model_to_dict
# from .models import Notification
# from channels.db import database_sync_to_async

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         print("I am connected")
#         self.group_name = 'public_room'
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def send_notification(self, event):
#         all_notifications = await self.get_notifications()
#         await self.send(text_data=json.dumps({'Xdata': event['Xdata'], 'all_notifications': all_notifications}))

#     @database_sync_to_async
#     def get_notifications(self):
#         queryset = Notification.objects.filter(is_seen=False)
#         # Convert model instances to dictionaries
#         serialized_notifications = [model_to_dict(notification) for notification in queryset]
#         return serialized_notifications
    
#     @database_sync_to_async
#     def update_notifications(self,notification_id):
#         notification = Notification.objects.get(pk=notification_id)
#         notification.is_seen = True
#         notification.save()

    
#     async def update_notification(self, event):
#         print(event)
#         notification_id=event['notification_id']
#         print(type())
#         print("In update notification"+str(notification_id))
#         try:
#             await self.update_notification(notification_id)
#             serialized_notifications = await self.get_notifications()
#             print(serialized_notifications)
#             print(type(serialized_notifications))
#             await self.send_notification({'Xdata': {'count': event['count'], 'all_notifications': serialized_notifications}})
#         except Notification.DoesNotExist:
#             print(f"Notification with id {notification_id} not found")

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict
from .models import *
from channels.db import database_sync_to_async
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync,sync_to_async
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = 'notify_%s' % self.room_name
        print(self.channel_layer)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("I am disconnected")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        print("In receive")
        print(text_data)
        print(type(text_data))
        d=json.loads(text_data)
        print(d)
        print(type(d))
        # breakpoint()
        if d['action']=="update_notification":
            await self.update_notification(d)
        elif d['action']=="send_notification_on_open":
               await self.send_notification_on_open(d)
        # for i in range(100):
        #     print(i)
        #     await self.send_message({'type':'send_message','message':{'count':i}})
        #     time.sleep(1)
    
    async def send_notification_on_open(self,d):
        room_name=d['roomName']
        user=await self.get_user(room_name)
        notifications = await self.get_notifications(user)
        await self.send_notification({'Xdata': {'count': len(notifications), 'all_notifications': notifications,'user':user},'context':'send_notification_on_open'})

    
    @sync_to_async
    @async_to_sync
    async def send_message(self,event):
        message = event["message"]
        print(f"In send message{str(message)}")
        await self.send(text_data=json.dumps({"message": message}))


    async def send_notification(self, event):
        print("In send notification")
        print(event)
        user=event['Xdata']['user']
        all_notifications = await self.get_notifications(user)
        print(all_notifications)
        if event['context'] in [
            'update_notification',
            "send_notification_on_open",
        ]:
                await self.send(text_data=json.dumps({
                'Xdata': {
                    'count': event['Xdata']['count']
                },
                'all_notifications': all_notifications,
            }))
        else:
                await self.send(text_data=json.dumps({
                'Xdata': {
                    'count': event['Xdata']['count'],
                    'current_notification': event['Xdata']['current_notification'],
                },
                'all_notifications': all_notifications,
            }))
        # print("In send notification")
        # print(event)
        # user=event['Xdata']['user']
        # print(user)
        # all_notifications = await self.get_notifications(user)
        # await self.send(text_data=json.dumps({'Xdata': event['Xdata'], 'all_notifications': all_notifications}))

        
    @database_sync_to_async
    def get_notifications(self,user):
        print("In get notification")
        print(user)
        queryset = Notification.objects.filter(user=user, is_seen=False)
        notifications_list = [
        {key: value for key, value in model_to_dict(notification).items() if key != 'user'}
        for notification in queryset
        ]
        print(notifications_list)
        return notifications_list
        # print("In get notification")
        # print(user)
        # queryset = Notification.objects.filter(user=user,is_seen=False)
        # x=[model_to_dict(notification) for notification in queryset]
        # print(x)
        # return x
    
    @database_sync_to_async
    def get_user(self,room_name):
        return User.objects.get(room__name=room_name)

    
    @database_sync_to_async
    def mark_notification_as_seen(self, user,notification_id):
        try:
            notification = Notification.objects.get(user=user,pk=notification_id)
            notification.is_seen = True
            notification.save()
        except Notification.DoesNotExist:
            print(f"Notification with id {notification_id} not found")

    async def update_notification(self, event):
        user=event
        notification_id = event['notificationId']
        room_name=event['roomName']
        print(type(notification_id))
        print(room_name)
        print(f"In update notification{str(notification_id)}")
        try:
            user=await self.get_user(room_name)
            await self.mark_notification_as_seen(user,notification_id)
            serialized_notifications = await self.get_notifications(user)
            print(serialized_notifications)
            print(type(serialized_notifications))
            await self.send_notification({'Xdata': {'count': len(serialized_notifications), 'all_notifications': serialized_notifications,'user':user},'context':'update_notification'})
        except Notification.DoesNotExist:
            print(f"Notification with id {notification_id} not found")
