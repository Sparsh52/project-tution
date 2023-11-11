from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *

class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'subject1', 'subject2', 'subject3', 'experience', 'gender','hourly_Rate','teacher_photo']

class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'institution_type', 'standard_or_semester', 'institution_name','gender','student_photo']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'student', 'rating', 'comment']

admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subject)
admin.site.register(Gender)
admin.site.register(Event)