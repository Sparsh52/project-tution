from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user','teacher_type','subject1', 'subject2', 'subject3', 'experience', 'gender','min_hourly_rate','max_hourly_rate','standard_or_semester','teacher_photo']

class StudentAdmin(admin.ModelAdmin):
    list_display = ['user','institution_type', 'standard_or_semester', 'institution_name','gender','student_photo']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'student', 'rating', 'comment']


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name','username','phone']

admin.site.register(User, UserAdmin)

admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(Gender)
admin.site.register(Event)
admin.site.register(Wallet)
admin.site.register(SessionRequest)
