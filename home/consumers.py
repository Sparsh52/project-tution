import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from django.forms.models import model_to_dict
from .models import *
from channels.db import database_sync_to_async
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync,sync_to_async
from django.urls import reverse
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = 'notify_%s' % self.room_name
        print(self.channel_layer)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
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

        
    @database_sync_to_async
    def get_notifications(self,user):
        print("In get notification")
        print(user)
        queryset = Notification.objects.filter(user=user, is_seen=False).order_by('-id')
        notifications_list = [
        {key: value for key, value in model_to_dict(notification).items() if key != 'user'}
        for notification in queryset
        ]
        print(notifications_list)
        return notifications_list
    
    
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

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["event_room_name"]
        self.room_group_name = 'event_%s' % self.room_name
        print(f"In connect event consumer{self.room_group_name}")
        print(self.room_group_name)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    @database_sync_to_async
    def get_user(self,room_name):
        return User.objects.get(room__name=room_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == 'create_event':
            await self.create_event(text_data_json)
        elif action == 'send_event_on_open':
            await self.send_event_on_open(text_data_json)
    
    async def send_event_on_open(self,d):
        room_name=d['eventroomName']
        teacher_name=d['teacherName']
        user=await self.get_user(room_name)
        events = await self.get_event(teacher_name)
        await self.send_events({'Events': {'count': len(events), 'all_events': events,'user':user},'context':'send_notification_on_open'})
    

    @database_sync_to_async
    def get_event(self, teacher_name):
        print("In get event")
        queryset = Event.objects.filter(created_by__user__name=teacher_name, booked_by__isnull=True)
        print(f"0th element{str(model_to_dict(queryset[0]))}")
        print(queryset[0])
        events_data = []
        for event in queryset:
            x=event.id
            event_dict = model_to_dict(event)
            print("In LOOP"+str(event_dict.keys()))
            event_dict['id']=str(x)
            event_dict['created_by'] = str(event_dict['created_by'])
            # event_dict['id'] = str(event_dict['id'])
            event_dict['booked_by'] = str(event_dict['booked_by']) if event_dict['booked_by'] else None
            event_dict['start_time'] = event_dict['start_time'].isoformat()
            event_dict['end_time'] = event_dict['end_time'].isoformat()
            events_data.append(event_dict)
        return events_data

    
    async def send_events(self, event):
        if event['context']=='send_notification_on_open':
            event_data = event['Events']
            all_events = event_data['all_events']
            await self.send(text_data=json.dumps({
                    'action': 'send_events',
                    'Events': {
                'count': event_data['count'],
                'all_events': all_events,
                },
            }))
        else:
            print("In send event else")
            print(event['Xdata'])
            count=event['Xdata']['count']
            print(count)
            print(model_to_dict(event['Xdata']['current_event']))
            all_events=await self.get_event(event['Xdata']['current_event'].created_by.user.name)
            await self.send(text_data=json.dumps({
                    'action': 'send_events',
                    'Events': {
                'count': count,
                'all_events': all_events,
                },
            }))