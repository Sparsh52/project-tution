# signals.py
from django.db.models.signals import post_save ,post_delete,pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .tasks import *
from django.forms.models import model_to_dict

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    # sourcery skip: avoid-builtin-shadow
    print("In signal notification created ")
    print(instance.user)
    if created:
        print(type(instance))
        x=model_to_dict(instance)
        id=x['user']
        print(type(id))
        user=User.objects.get(id=id)
        print(user)
        teacher=None
        student=None
        try:
            student=Student.objects.get(user=instance.user)
        except Student.DoesNotExist:
            teacher=Teacher.objects.get(user=instance.user)
        print(teacher)
        print(student)
        room_name = user.room.name
        print(room_name)
        count= Notification.objects.filter(user=x['user'], is_seen=False).count()
        if teacher is not None:
            broadcast_notification_teacher.delay(x,room_name,count)
        else:
            broadcast_notification_student(x,room_name,count)
        # breakpoint()
        # user = instance.user
        # print(user)
        # room_name = user.room.name
        # print(room_name)
        # channel_layer = get_channel_layer()
        # print(channel_layer)
        # room_group_name = 'notify_%s' % room_name
        # print(room_group_name)
        # data = {'count': Notification.objects.filter(user=user, is_seen=False).count(),'current_notification':instance.message,'user':user}
        # async_to_sync(channel_layer.group_send)(
        #         room_group_name, {
        #             "type": "send_notification",
        #             "Xdata":data,
        #             "context":"notification_created"
        #     }
        # )


@receiver(post_save, sender=Teacher)
def teacher_created_or_updated(sender, instance, created, **kwargs):
    user = instance.user
    name = user.name
    if created:
        Notification.objects.create(user=user, is_seen=False, message=f"🎉 Welcome, {name}! 🎉")
    else:
        original_values = instance.__class__.objects.filter(pk=instance.pk).values().first()

        if updated_fields := [
            field
            for field in instance.__dict__
            if original_values.get(field) != getattr(instance, field)
        ]:
            updated_message =updated_message = "🎺 You have successfully updated your profile.🎺 "
        else:
            updated_message = f"Profile updated for {name}."
        Notification.objects.create(user=user, is_seen=False, message=updated_message)
@receiver(post_save, sender=Student)
def student_created_or_updated(sender, instance, created, **kwargs):
    user = instance.user
    name = user.name
    if created:
        Notification.objects.create(user=user, is_seen=False, message=f"🎉 Welcome, {name}! 🎉")
    else:
        original_values = instance.__class__.objects.filter(pk=instance.pk).values().first()
        if original_values and any(
            original_values.get(field) != getattr(instance, field)
            for field in instance.__dict__
        ):
            updated_message = "🎺 You have successfully updated your profile.🎺 "
        else:
            updated_message = f"Profile updated for {name}."
        Notification.objects.create(user=user, is_seen=False, message=updated_message)

@receiver(post_save, sender=Event)
def event_created_or_booked(sender, instance, created, **kwargs):
    # sourcery skip: replace-interpolation-with-fstring
    print("In event created or booked_by")
    if created:
        teacher = instance.created_by.user
        creator_name = teacher.name
        Notification.objects.create(
            user=teacher,
            is_seen=False,
            message=f"🎉 Event created by {creator_name}: {instance.title}. Start Time: {instance.start_time}, End Time: {instance.end_time}. 🎉"
        )
    elif instance.booked_by:
        student = instance.booked_by.user
        booker_name = student.name
        Notification.objects.create(
            user=student,
            is_seen=False,
            message=f"🎉 Event booked by {booker_name}: {instance.title}. Start Time: {instance.start_time}, End Time: {instance.end_time}, Cost: {instance.event_cost}. 🎉"
        )
        teacher = instance.created_by.user
        creator_name = teacher.name
        Notification.objects.create(
            user=teacher,
            is_seen=False,
            message=f"🎉 Event {instance.title} has been booked by {instance.booked_by.user.name}. 🎉"
        )

@receiver(post_save, sender=SessionRequest)
def session_request_created(sender, instance, created, **kwargs):
    print(f"Session created{instance}")
    if created:
        teacher = instance.teacher.user
        student = instance.student.user
        Notification.objects.create(
            user=student,
            is_seen=False,
            message=f"🎉 Your session request to {instance.teacher.user.name} has been sent. 🎉"
        )
        Notification.objects.create(
            user=teacher,
            is_seen=False,
            message=f"🎉 New session request from {instance.student.user.name}. 🎉"
        )

@receiver(post_delete, sender=Event)
def event_deleted(sender, instance, **kwargs):
    teacher = instance.created_by.user
    student = instance.booked_by.user if instance.booked_by else None
    Notification.objects.create(
        user=teacher,
        is_seen=False,
        message=f"🚨 Event {instance.title} has been canceled. 🚨"
    )
    if student:
        Notification.objects.create(
            user=student,
            is_seen=False,
            message=f"🚨 Event {instance.title} has been canceled. 🚨"
        )
