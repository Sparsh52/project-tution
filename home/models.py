from django.db import models
# from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.http import HttpResponse
import random
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.conf import settings
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
User = settings.AUTH_USER_MODEL

class UserManager(BaseUserManager):
    def validate_field(self, field_name, value):
        allowed_characters_email=re.compile('[_!#$%^&*()<>?/\|}{~:]')
        allowed_characters_field=re.compile('[\d@_!#$%^&*()<>?/\|}{~:]')
        if field_name=='email' and allowed_characters_email.search(value) is not None:
            raise ValidationError(_('email contains invalid characters.'),code='invalid_characters')
        if field_name=='name' and allowed_characters_field.search(value) is not None:
            raise ValidationError(_(f'{field_name} contains invalid characters.'),code='invalid_characters')
        if field_name=='phone':
            phone_digits = ''.join(c for c in value if c.isdigit())
            if len(phone_digits) != 10:
                raise ValidationError(_('Phone number must contain 10 digits.'), code='invalid_phone')
        return True
    
    def create_user(self, email,password=None, name=None, username=None,phone=None):
        if not email:
            raise ValueError('Users must have an email address')
        if self.model.objects.filter(email=email).exists():
            raise ValidationError(_('A user with this email address already exists.'), code='duplicate_email')
        if self.model.objects.filter(name=name).exists():
            raise ValidationError(_('A user with this name already exists.'), code='duplicate_name')
        if self.model.objects.filter(username=username).exists():
            raise ValidationError(_('A user with this username already exists.'), code='duplicate_username')
        if self.model.objects.filter(phone=phone).exists():
            raise ValidationError(_('A user with this phone number already exists.'), code='duplicate_phone')
        if self.validate_field('email',email) and self.validate_field('name',name) and self.validate_field('username',username) and self.validate_field('phone',phone):
            user = self.model(
            email=self.normalize_email(email),
            name=name,
            username=username,
            phone=phone,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    phone=models.CharField(max_length=255, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    @property
    def get_full_name(self):
        return self.name
    
    @property
    def get_username(self):
        return self.username or self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

   
   
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
    TYPE_CHOICES = [
        ('College', 'College'),
        ('School', 'School'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    teacher_type=models.CharField(max_length=10, choices=TYPE_CHOICES, blank=False,null=False)
    subject1 = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers_subject1')
    subject2 = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers_subject2')
    subject3 = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teachers_subject3')
    experience = models.IntegerField()
    gender = models.ForeignKey(Gender,on_delete=models.CASCADE)
    min_hourly_rate = models.IntegerField()
    max_hourly_rate = models.IntegerField()
    teacher_image=models.ImageField(upload_to="teacher",blank=True, null=True)
    registered_students = models.ManyToManyField('Student', related_name='teachers', blank=True)
    wallet=models.ForeignKey(Wallet,related_name='wallet_teacher',on_delete=models.CASCADE,default=None)
    standard_or_semester=models.IntegerField(blank=False,null=False)
    
    @property
    def average_hourly_rate(self):
        return (self.min_hourly_rate + self.max_hourly_rate)//2

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
        return self.user.name

class Student(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    INSTITUTION_TYPES = [
        ('School', 'School'),
        ('University', 'University'),
    ]
    institution_type = models.CharField(max_length=10, choices=INSTITUTION_TYPES, blank=False)
    standard_or_semester=models.IntegerField(blank=False,null=False)
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
        return self.user.name


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
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    
    def get_available_url(self, user_type):
        if user_type != 'student':
            if self.booked_by is None:
                url=reverse('available_slot_teacher')
            else:
                url=reverse('booked_slots_teacher')
            return (f'<a href="{url}" style="color: white;">{self.title}</a>',self.title,self.created_by,self.booked_by)
        url = reverse('available_slots_student', args=[self.created_by.id])
        return (f'<a href="{url}" style="color: white;">{self.title}</a>',self.title,self.created_by,self.booked_by)
    

