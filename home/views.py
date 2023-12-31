import contextlib
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
from django.contrib.auth import login,authenticate,logout
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
def home(request):
   if request.method=="POST":
      username=request.POST.get('username')
      password=request.POST.get('password')
      if not User.objects.filter(username=username).exists():
         messages.error(request, 'Invalid Username')
         return redirect("/register/")
      user = authenticate(username = username,password = password)
      if user is None:
         messages.error(request, 'Invalid Password')
         return redirect('home')
      else:
         login(request,user)
          # Check if the user is a teacher or student
         with contextlib.suppress(Teacher.DoesNotExist):
            teacher = Teacher.objects.get(user=user)
            return HttpResponse('IsTeacher')
         with contextlib.suppress(Student.DoesNotExist):
            student = Student.objects.get(user=user)
            return redirect('/student-profile/')
   return render(request,"login.html")

def add_feedback(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        feedback = Feedback.objects.create(
            teacher=teacher,
            student=request.user,
            comment=comment,
            rating=rating
        )
        messages.success(request, 'Feedback added successfully!')
        return redirect('teacher_profile', teacher_id=teacher_id)
    return render(request, 'add_feedback.html', {'teacher': teacher})


def student_profile(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, 'student_profile.html', context)

def teachers_list(request):
   queryset = Teacher.objects.all()
   search_query = request.GET.get('search_query')
   hourly_price = request.GET.get('hourlyPrice')
   experience = request.GET.get('experience')
   if search_query := request.GET.get('search_query'):
      subjects_filter= (Q(subject1__subject__icontains=search_query) | Q(subject2__subject__icontains=search_query) | Q(subject3__subject__icontains=search_query))
      username_filter=(Q(user__username=search_query))
      queryset = queryset.filter(subjects_filter|username_filter)
   if hourly_price:
      queryset = queryset.filter(hourly_Rate__lte=hourly_price)
   if experience:
      queryset = queryset.filter(experience__gte=experience)
   context = {'teachers': queryset}
   return render(request, 'teacherlist.html', context)

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
    if Teacher.objects.filter(user=user).exists():
        messages.error(request, 'You are already registered as a teacher.')
        return redirect('home')
    if request.method == 'POST':
      return extracted_from_register_Teacher(request, user)
    return render(request, 'teacherregistration.html')


def register_student(request):
   reg_type = request.session.get('reg_type')
   user_id = request.session.get('user_id')
   user = User.objects.get(id=user_id)
   if Student.objects.filter(user=user).exists():
      messages.error(request, 'You are already registered as a student.')
      return redirect('home')
   if request.method == 'POST':
      return extracted_from_register_student(request,user)
   return render(request,"studentregistration.html")



def teacher_profile(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    feedbacks = teacher.feedbacks.all()
    context = {
        'teacher': teacher,
        'feedbacks': feedbacks,
    }
    return render(request, 'teacher_profile.html', context)




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

def extracted_from_register_Teacher(request, user):
    data = request.POST
    hourly_Rate=data['hourly_rate']
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
            teacher_image=img,
            hourly_Rate=hourly_Rate
        )
    else:
        Teacher.objects.create(
            user=user,
            phone=phone,
            subject1=sub_instance_1,
            subject2=sub_instance_2,
            subject3=sub_instance_3,
            experience=exp,
            gender=gender_instance,
            hourly_Rate=hourly_Rate
        )
    return redirect('home')


def extracted_from_register_student(request,user):
   phone = request.POST['phone']
   ins_type = request.POST['ins_type']
   standard_or_semester = request.POST.get('standard') or request.POST.get('semester')
   institution_name = request.POST['institution_name']
   gender = request.POST['gender']
   img = request.FILES.get('student_image')
   gender_instance,_=Gender.objects.get_or_create(gender=gender.title())
   if img is not None:
      Student.objects.create(
         user=user,
         phone=phone,
         institution_type=ins_type,
         standard_or_semester=standard_or_semester,
         institution_name=institution_name,
         gender=gender_instance,
         student_image=img
      )
   else:
      Student.objects.create(
            user=user,
            phone=phone,
            institution_type=ins_type,
            standard_or_semester=standard_or_semester,
            institution_name=institution_name,
            gender=gender_instance
      )
      return redirect('home')
