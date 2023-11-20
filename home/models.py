from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.http import HttpResponse
import random

# Create your models here.
class Wallet(models.Model):
    balance = models.IntegerField(default=0)
    def deposit(self, amount):
        self.balance += amount
        self.save()
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

class Subject(models.Model):
    subject=models.CharField(max_length=100)
    def __str__(self):
        return self.subject

class Gender(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=False,null=False)
    def __str__(self):
        return self.gender

class Teacher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100, blank=False)
    subject1 = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers_subject1')
    subject2 = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers_subject2')
    subject3 = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers_subject3')
    experience = models.IntegerField()
    gender = models.ForeignKey(Gender,on_delete=models.CASCADE)
    hourly_Rate=models.IntegerField()
    teacher_image=models.ImageField(upload_to="teacher",blank=True, null=True)
    registered_students = models.ManyToManyField('Student', related_name='teachers', blank=True)
    wallet=models.ForeignKey(Wallet,related_name='wallet_teacher',on_delete=models.CASCADE,default=None)

    
    @property
    def teacher_photo(self):
        if self.teacher_image:
            return mark_safe(f'<img src="{self.teacher_image.url}" width="100" />')
        default_image = 'default_male_image.jpg' if self.gender.gender == 'Male' else 'default_female_image.png'
        return mark_safe(f'<img src="/media/teacher/{default_image}" width="100" />')
    
    @property
    def teacher_image_url(self):
        if self.teacher_image:
            return self.teacher_image.url
        default_image = 'default_male_image.jpg' if self.gender.gender == 'Male' else 'default_female_image.png'
        return f"/media/teacher/{default_image}"

    


    def __str__(self):
        return self.user.username

class Student(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100, blank=False)
    INSTITUTION_TYPES = [
        ('School', 'School'),
        ('University', 'University'),
    ]
    institution_type = models.CharField(max_length=10, choices=INSTITUTION_TYPES, blank=False)
    standard_or_semester=models.CharField(max_length=100,blank=False,null=False)
    institution_name=models.CharField(max_length=100,blank=False,null=False)
    gender = models.ForeignKey(Gender,on_delete=models.CASCADE)
    student_image=models.ImageField(upload_to="student",blank=True, null=True)
    wallet=models.ForeignKey(Wallet,related_name='wallet_student',on_delete=models.CASCADE,default=None)

    
    @property
    def student_photo(self):
        if self.student_image:
            return mark_safe(f'<img src="{self.student_image.url}" width="100" />')
        default_image = 'default_male_image.jpg' if self.gender.gender == 'Male' else 'default_female_image.png'
        return mark_safe(f'<img src="/media/teacher/{default_image}" width="100" />')
    
    @property
    def student_image_url(self):
        if self.student_image:
            return self.student_image.url
        default_image = 'default_male_image.jpg' if self.gender.gender == 'Male' else 'default_female_image.png'
        return f"/media/teacher/{default_image}"
    def __str__(self):
        return self.user.username


class Feedback(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,related_name="feedbacks")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    def get_stars(self):
        return range(self.rating)
    def _str_(self):
        return f"Feedback for {self.teacher.user.username} by {self.student.username}"

class Event(models.Model):
    created_by=models.ForeignKey(Teacher,on_delete=models.CASCADE)
    booked_by=models.ForeignKey(Student,on_delete=models.CASCADE,blank=True,null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def get_available_url(self, user_type):
        if user_type != 'student':
            url=reverse('available_slot_teacher')
            return (f'<a href="{url}" style="color: black;">{self.title}</a>',self.title,self.created_by)
        url = reverse('available_slots_student', args=[self.created_by.id])
        return (f'<a href="{url}" style="color: black;">{self.title}</a>',self.title,self.created_by)
    

