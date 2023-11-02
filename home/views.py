from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistration
from django.contrib.auth.models import User
from .models import *


def home(request):
   return render(request,"login.html")

def register(request):
   fm = UserRegistration()
   if request.method == 'POST':
      fm = UserRegistration(request.POST)
      data = request.POST
      if fm.is_valid():
         return extracted_from_home(fm, data, request)
      for field, errors in fm.errors.items():
         for error in errors:
            messages.error(request, f"{field}: {error}")
      return redirect('home')
   return render(request, 'userregistration.html', {'form': fm})


# def verify_email(email, name):
#     subject = 'Welcome to GFG world'
#     message = f'Hi {name}, thank you for registering in GeeksforGeeks.'
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [email]
#     send_mail(subject, message, email_from, recipient_list)

def register_teacher(request):
   return render(request,"teacherregistration.html")

def register_student(request):
   return render(request,"studentregistration.html")





#----------------------------------------Helpers-----------------------------------------------#

def extracted_from_home(fm, data, request):
   name = fm.cleaned_data['name']
   email = fm.cleaned_data['email']
   password = fm.cleaned_data['password']
   reg_type = data['reg_type']
   if User.objects.filter(username=name).exists():
      messages.error(request, 'User with this username already exists.')
   elif Teacher.objects.filter(user__username=name).exists():
      messages.error(request, 'Exists as Teacher')
   elif Student.objects.filter(user__username=name).exists():
      messages.error(request, 'Exists as Student')
   elif User.objects.filter(email=email).exists():
      messages.error(request, 'Email is already registered.')
   elif len(password) < 8:
      messages.error(request, 'Password must be at least 8 characters long.')
   else:
      user = User.objects.create_user(username=name, email=email, password=password)
      request.session['reg_type'] = reg_type
      request.session['user_id'] = user.id
      return (
            redirect('/register-teacher/') if reg_type == "Teacher"
            else redirect('/register-student/')
        )
      return redirect('home')