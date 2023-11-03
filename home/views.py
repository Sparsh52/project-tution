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
    reg_type = request.session.get('reg_type')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)

    # Check if the user is already registered as a teacher
    if Teacher.objects.filter(user=user).exists():
        messages.error(request, 'You are already registered as a teacher.')
        return redirect('home')
    if request.method == 'POST':
      return _extracted_from_registerTeacher_6(request, user)
    return render(request, 'teacherregistration.html')

# TODO Rename this here and in `registerTeacher`
def _extracted_from_registerTeacher_6(request, user):
    data = request.POST
    phone = data['phone']
    sub1 = data['sub1']
    sub2 = data['sub2']
    sub3 = data['sub3']
    exp = data['exp']
    gender = data['gender']
    img = request.FILES.get('teacher_image')
    if img is not None:
      print('Yeah!')
    else:
      print('Nah man!')
    gender_instance,_=Gender.objects.get_or_create(gender=gender.title())
    sub_instance_1, _ = Subject.objects.get_or_create(subject=sub1.title())
    sub_instance_2, _ = Subject.objects.get_or_create(subject=sub2.title())
    sub_instance_3, _ = Subject.objects.get_or_create(subject=sub3.title())
    if img is not None:
        Teacher.objects.create(
            user=user,
            phone=phone,
            subject1=sub_instance_1,
            subject2=sub_instance_2,
            subject3=sub_instance_3,
            experience=exp,
            gender=gender_instance,
            teacher_image=img
        )
    else:
        Teacher.objects.create(
            user=user,
            phone=phone,
            subject1=sub_instance_1,
            subject2=sub_instance_2,
            subject3=sub_instance_3,
            experience=exp,
            gender=gender_instance
        )
    return redirect('home')

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
      # messages.success(request, 'I have taken notice!')
      request.session['reg_type'] = reg_type
      request.session['user_id'] = user.id
      return (
            redirect('/register-teacher/') if reg_type == "Teacher"
            else redirect('/register-student/')
        )