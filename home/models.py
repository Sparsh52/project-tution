from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
# Create your models here.


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
    teacher_image=models.ImageField(upload_to="teacher",blank=True, null=True)
    
    
    @property
    def teacher_photo(self):
        if self.teacher_image:
            return mark_safe(f'<img src="{self.teacher_image.url}" width="100" />')
        default_image = 'default_male_image.jpg' if self.gender.gender == 'Male' else 'default_female_image.png'
        return mark_safe(f'<img src="/media/teacher/{default_image}" width="100" />')

    


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
    def __str__(self):
        return self.user.username