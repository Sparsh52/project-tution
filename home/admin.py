from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id','user','teacher_type','subject1', 'subject2', 'subject3', 'experience', 'gender','min_hourly_rate','max_hourly_rate','standard_or_semester','teacher_photo']

class StudentAdmin(admin.ModelAdmin):
    list_display = ['id','user','institution_type', 'standard_or_semester', 'institution_name','gender','student_photo']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id','teacher', 'student', 'rating', 'comment']


class UserAdmin(admin.ModelAdmin):
    list_display = ['id','email', 'name','username','phone','room']

class SessionAdmin(admin.ModelAdmin):
    list_display = ['id','student', 'teacher','start_time','end_time','title','message','requested_cost']


class eventAdmin(admin.ModelAdmin):
    list_display = ['id','created_by', 'booked_by','title','description','start_time','end_time','event_cost']

admin.site.register(User, UserAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(Gender)
admin.site.register(Event,eventAdmin)
admin.site.register(Wallet)
admin.site.register(SessionRequest,SessionAdmin)
admin.site.register(NotifyRoom)
admin.site.register(Notification)