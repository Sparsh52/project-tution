
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from tut.celery import app
from django.forms.models import model_to_dict
from asgiref.sync import sync_to_async
from celery import shared_task
import asyncio
import nest_asyncio
from channels.db import database_sync_to_async
nest_asyncio.apply()

@shared_task(bind = True)
def broadcast_notification_student(self,instance,room_name,count):
    # sourcery skip: replace-interpolation-with-fstring
    print(f"In broadcast Notification student {instance}")
    room_name = room_name
    print(room_name)
    channel_layer = get_channel_layer()
    print(channel_layer)
    room_group_name = 'notify_%s' % room_name
    data = {'count': count,'current_notification':instance['message'],'user':str(instance['user'])}
    loop=None
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send(room_group_name,{
                "type": "send_notification",
                "Xdata":data,
                "context":"notification_created"
    }))
    
@shared_task(bind = True)
def broadcast_notification_teacher(self,instance,room_name,count):
    # sourcery skip: replace-interpolation-with-fstring
    print(f"instance is{str(instance)}")
    print(f"In broadcast Notification teacher{instance}")
    room_name = room_name
    print(room_name)
    channel_layer = get_channel_layer()
    print(channel_layer)
    room_group_name = 'notify_%s' % room_name
    data = {'count': count,'current_notification':instance['message'],'user':str(instance['user'])}
    loop=None
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send(room_group_name,{
                "type": "send_notification",
                "Xdata":data,
                "context":"notification_created"
    }))
