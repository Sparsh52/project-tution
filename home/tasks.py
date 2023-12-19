
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from tut.celery import app
from django.forms.models import model_to_dict

@app.task(bind = True)
def broadcast_notification(self,instance):
    # sourcery skip: replace-interpolation-with-fstring
    print(f"In broadcast Notification{instance}")
    print(instance)
    user_id = instance['user']
    user=User.objects.get(id=user_id)
    print(user)
    print(user.room)
    room_name = user.room.name
    print(room_name)
    channel_layer = get_channel_layer()
    print(channel_layer)
    room_group_name = 'notify_%s' % room_name
    print(room_group_name)
    data = {'count': Notification.objects.filter(user=user, is_seen=False).count(),'current_notification':instance['message'],'user':user}
    async_to_sync(channel_layer.group_send)(
            room_group_name, {
                "type": "send_notification",
                "Xdata":data,
                "context":"notification_created"
        }
    )


@app.task(bind=True)
def broadcast_event(self,instance):
    print(f"In broadcast Event{instance}")
    print(instance)