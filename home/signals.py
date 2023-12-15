# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync,sync_to_async
# from .models import *
# import threading



# @receiver(post_save, sender=Notification)
# def notification_created(sender, instance, created, **kwargs):
#     print(f"In signal{instance.message}")
#     if created:
#         channel_layer = get_channel_layer()
#         notification_objs = Notification.objects.filter(is_seen=False).count()
#         data = {'count': notification_objs, 'current_notification':instance.message}
#         print(data)
#         print(instance)
#         room_name="walt_room_"
#         room_group_name = 'notify_%s' % room_name
#         async_to_sync(channel_layer.group_send)(
#             room_group_name,{
#                 "type": "send_notification",
#                 "Xdata":data
#         })
#         # async_to_sync(channel_layer.group_send)(room_group_name, data)

# @receiver(post_save,sender=Student)
# def student_created(sender, instance, created, **kwargs):
#     pass


# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Student)
def student_created(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        name = user.name
        Notification.objects.create(user=user, is_seen=False, message=f"Welcome {name}")
      
@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    print("In signal notification created ")
    if created:
        user = instance.user
        print(user)
        room_name = user.room.name
        print(room_name)
        channel_layer = get_channel_layer()
        print(channel_layer)
        room_group_name = 'notify_%s' % room_name
        print(room_group_name)
        data = {'count': Notification.objects.filter(user=user, is_seen=False).count(),'current_notification':instance.message,'user':user}
        async_to_sync(channel_layer.group_send)(
            room_group_name, {
                "type": "send_notification",
                "Xdata":data,
                "context":"notification_created"
            }
        )
