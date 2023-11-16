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
from .utils import Calendar
from datetime import datetime, timedelta, date
import calendar
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@never_cache
def home(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        try:
            # Attempt to get the Teacher profile
            teacher = Teacher.objects.get(user=request.user)
            return redirect('/teacher-profile-teacher/')
        except Teacher.DoesNotExist:
            try:
                # Attempt to get the Student profile
                student = Student.objects.get(user=request.user)
                return redirect('/student-profile/')
            except Student.DoesNotExist:
                # Handle the case where the user is authenticated but not a Teacher or Student
                messages.error(request, 'Invalid user type')
                return redirect('home')

    # Handle POST requests for login
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect("/register/")
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('home')
        else:
            login(request, user)
            try:
                teacher = Teacher.objects.get(user=user)
                return redirect('/teacher-profile-teacher/')
            except Teacher.DoesNotExist:
                try:
                    student = Student.objects.get(user=user)
                    return redirect('/student-profile/')
                except Student.DoesNotExist:
                    messages.error(request, 'Invalid user type')
                    return redirect('home')
    return render(request, "login.html")


@never_cache
@login_required(login_url='home')
def teacher_profile_teacher(request):
   teacher = get_object_or_404(Teacher, user=request.user)
   return render(request, 'teacher_profile_teacher.html', {'teacher': teacher})

@never_cache
@login_required(login_url='home')
def registered_students_teacher(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    students = teacher.registered_students.all()
    return render(request, 'registered_students.html', {'students': students, 'teacher': teacher})


@never_cache
@login_required(login_url='home')
def student_profile_teacher(request,student_id):
   student=Student.objects.get(id=student_id)
   return render(request,'student_profile_teacher.html',{'student':student})


@never_cache
@login_required(login_url='home')
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


@never_cache
@login_required(login_url='home')
def student_profile(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, 'student_profile.html', context)


@never_cache
@login_required(login_url='home')
def teachers_list(request):
   student = Student.objects.get(user=request.user)
   registered_teachers_ids = student.teachers.values_list('id', flat=True)
   queryset = Teacher.objects.exclude(id__in=registered_teachers_ids)
   search_query = request.GET.get('search_query')
   hourly_price = request.GET.get('hourlyPrice')
   experience = request.GET.get('experience')
   if search_query:
      subjects_filter = (Q(subject1__subject__icontains=search_query) | 
                           Q(subject2__subject__icontains=search_query) | 
                           Q(subject3__subject__icontains=search_query))
      username_filter = Q(user__username=search_query)
      queryset = queryset.filter(subjects_filter | username_filter)
   if hourly_price:
      queryset = queryset.filter(hourly_Rate__lte=hourly_price)
   if experience:
      queryset = queryset.filter(experience__gte=experience)
   context = {'teachers': queryset}
   return render(request, 'teacherlist.html', context)

@never_cache
def register(request):
   fm = UserRegistration()
   if request.method == 'POST':
      fm = UserRegistration(request.POST)
      data = request.POST
      if fm.is_valid():
         try:
            return extracted_from_home(fm, data, request)
         except Exception as e:
            print("Something Wrong happend",e)
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

@never_cache
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

@never_cache
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

@never_cache
@login_required(login_url='home')
def teacher_profile(request, teacher_id):
    student = Student.objects.get(user=request.user)
    teacher = get_object_or_404(Teacher, id=teacher_id)
    feedbacks = teacher.feedbacks.all()
    context = {
        'teacher': teacher,
        'feedbacks': feedbacks,
        'student':student
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

@never_cache
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
   
@never_cache
@login_required(login_url='home')
def book_session(request,teacher_id):
   try:
      student = Student.objects.get(user=request.user)
      user_type = "student"
   except Student.DoesNotExist:
      user_type = "teacher"
   teacher = get_object_or_404(Teacher, id=teacher_id)
   month_param = request.GET.get('month', None)
   d = get_date(month_param)
   cal = Calendar(d.year, d.month)
   html_cal = cal.formatmonth(user_type,withyear=True)
   context = {
        'calendar': mark_safe(html_cal),
        'prev_month': prev_month(d),
        'next_month': next_month(d),
        'teacher':teacher,
        'user_type':user_type
    }
   print(teacher)
   return render(request, 'calendar.html', context)


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = f'month={str(prev_month.year)}-{str(prev_month.month)}'
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = f'month={str(next_month.year)}-{str(next_month.month)}'
    return month

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.now()

@never_cache
@login_required(login_url='home')
def register_under_teacher(request,teacher_id):
   teacher=get_object_or_404(Teacher, id=teacher_id)
   student = Student.objects.get(user=request.user)
   teacher.registered_students.add(student)
   return redirect('/registered-teachers-list/')

@never_cache
@login_required(login_url='home')
def registered_teachers_list(request):
   student = Student.objects.get(user=request.user)
   queryset = student.teachers.all()
   context = {'teachers': queryset}
   return render(request, 'teacher_registered_list.html', context)


@never_cache
@login_required(login_url='home')
def event(request, teacher_id, event_id=None):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    instance = get_object_or_404(Event, pk=event_id) if event_id else Event()
    student=None
    try:
        student = Student.objects.get(user=request.user)
        user_type = "student"
    except Student.DoesNotExist:
        user_type = "teacher"
    if student is None:
       form = EventForm(request,user_type,data=request.POST or None, instance=instance,initial={'created_by':teacher})
    else:
       print(student)
       form = EventForm(request,user_type,data=request.POST or None, instance=instance,initial={'booked_by':student})
   #  form = EventForm(requestuser_type,data=request.POST or None, instance=instance,initial={'created_by':teacher})
    if request.POST and form.is_valid():
        form.save()
        return redirect(reverse('book_session', kwargs={'teacher_id': teacher.id}))
    if event_id is None:
        return render(request, 'event.html', {'form': form, 'teacher': teacher,'user_type':user_type})
    return render(request, 'event.html', {'form': form, 'instance': instance, 'teacher': teacher,'user_type':user_type})

@never_cache
@login_required(login_url='home')
def available_slots_student(request, teacher_id):
    teacher=get_object_or_404(Teacher,id=teacher_id)  
    teacher_events = Event.objects.filter(created_by__id=teacher_id, booked_by__isnull=True)
    return render(request, 'available_slots.html', {'teacher_events': teacher_events,'teacher':teacher})

@never_cache
@login_required(login_url='home')
def booked_slots_students(request):
   student = Student.objects.get(user=request.user)
   booked_events = Event.objects.filter(booked_by_id=student.id)
   context = {
        'booked_events': booked_events,
    }
   return render(request, 'booked_slots.html', context)
@never_cache
@login_required(login_url='home')
def available_slot_teacher(request):
   teacher=Teacher.objects.get(user=request.user)
   unbooked_events=Event.objects.filter(created_by=teacher, booked_by__isnull=True)
   return render(request, 'unbooked_events.html', {'teacher': teacher, 'unbooked_events': unbooked_events})

@never_cache
@login_required(login_url='home')
def booked_slots_teacher(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    events = Event.objects.filter(created_by=teacher, booked_by__isnull=False)
    return render(request, 'booked_slots_teacher.html', {'events': events, 'teacher': teacher})

@never_cache
@login_required(login_url='home')
def delete_event(request, event_id):
   event = get_object_or_404(Event, id=event_id)
   if request.method == 'POST':
      event.delete()
      return redirect('/teacher-profile-teacher/')
   context = {'event': event}
   return render(request, 'delete_event.html', context)

@never_cache
def logout_page(request):
   logout(request)
   return redirect('home')