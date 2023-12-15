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
# from django.contrib.auth.models import User
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
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
import uuid
from .decorators import *
from django.template.loader import render_to_string

@never_cache
@logindec
def home(request):
    next_page = request.GET.get('next', request.META.get('HTTP_REFERER'))
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Invalid Username')
            return redirect("/register/")
        user = authenticate(email=email, password=password)
        if user is None:
            messages.error(request, 'Invalid Password')
            return redirect('home')
        else:
            print("Before Login")
            print(user)
            login(request, user)
            try:
                print("LOL6")
                teacher = Teacher.objects.get(user=user)
                if next_page is not None and next_page!='http://127.0.0.1:8000/':
                    return redirect(next_page)
                else:
                    return redirect('teacher-profile-teacher/')
            except Teacher.DoesNotExist:
                try:
                    print("LOL5")
                    student = Student.objects.get(user=user)
                    if next_page is not None and next_page!='http://127.0.0.1:8000/':
                        return redirect(next_page)
                    else:
                        return redirect('/student-profile/')
                except Student.DoesNotExist:
                    messages.error(request, 'Invalid user type')
                    return render(request,"login.html")
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
    student=Student.objects.get(user=request.user)
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
    return render(request, 'add_feedback.html', {'teacher': teacher,'student':student})


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
   subject = request.GET.get('subject')
   teacher_type = request.GET.get('teacherType')
   standard_or_semester = request.GET.get('standard_or_semester')
   if search_query:
      subjects_filter = (Q(subject1__subject__icontains=search_query) | 
                           Q(subject2__subject__icontains=search_query) | 
                           Q(subject3__subject__icontains=search_query))
      username_filter = Q(user__username__icontains=search_query)
      queryset = queryset.filter(subjects_filter | username_filter)
   if hourly_price:
      queryset = queryset.filter(min_hourly_rate__lte=hourly_price)
   if experience:
      queryset = queryset.filter(experience__gte=experience)
   if subject:
    subjects_filter = (Q(subject1__subject__icontains=subject) | Q(subject2__subject__icontains=subject) | Q(subject3__subject__icontains=subject))
    queryset = queryset.filter(subjects_filter) 
   if teacher_type:
    queryset = queryset.filter(teacher_type=teacher_type)
   if standard_or_semester:
        queryset = queryset.filter(standard_or_semester__lte=standard_or_semester)
   paginator = Paginator(queryset, 2) 
   page_number = request.GET.get("page")
   page_obj = paginator.get_page(page_number)
   print(page_obj)
   context = {'teachers': page_obj,'student':student}
   return render(request, 'teacherlist.html', context)

@never_cache
def register(request):
   fm = UserRegistration()
   if request.method == 'POST':
      fm = UserRegistration(request.POST)
      data = request.POST
      if fm.is_valid():
         try:
            print("In register")
            return extracted_from_home(fm, data, request)
         except Exception as e:
            print("Something Wrong happend",e)
      for field, errors in fm.errors.items():
         for error in errors:
            messages.error(request, f"{field}: {error}")
      return redirect('home')
   return render(request, 'userregistration.html', {'form': fm})




@never_cache
def register_teacher(request):
    reg_type = request.session.get('reg_type')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if Teacher.objects.filter(user=user).exists():
        messages.error(request, 'You are already registered as a teacher.')
        return redirect('home')
    if request.method == 'POST':
      try:
         return extracted_from_register_Teacher(request, user)
      except Exception as e:
         return redirect("home")
    return render(request, 'teacherregistration.html')

@never_cache
def register_student(request):
   print("In Student")
   reg_type = request.session.get('reg_type')
   user_id = request.session.get('user_id')
   user = User.objects.get(id=user_id)
   if Student.objects.filter(user=user).exists():
        messages.error(request, 'You are already registered as a student.')
        return redirect('home')
   if request.method == 'POST':
      try:
         return extracted_from_register_student(request,user)
      except Exception as e:
         return redirect("home")
   return render(request,"studentregistration.html")

@never_cache
@login_required(login_url='home')
def teacher_profile(request, teacher_id):
    student = Student.objects.get(user=request.user)
    teacher = get_object_or_404(Teacher, id=teacher_id)
    print(teacher.id)
    feedbacks = teacher.feedbacks.all()
    context = {
        'teacher': teacher,
        'feedbacks': feedbacks,
        'student':student
    }
    return render(request, 'teacher_profile.html', context)


def extracted_from_home(fm, data, request):
#    print('User in extracted_from_home:', user)
    name = fm.cleaned_data['name']
    username = fm.cleaned_data['username']
    email = fm.cleaned_data['email']
    password = fm.cleaned_data['password']
    reg_type = data['reg_type']
    phone=data['phone']
    room = f"{name}_room_"
    notify_room=NotifyRoom.objects.create(name=room)
    user = User.objects.create_user(name=name, username=username,email=email,phone=phone,password=password,room=notify_room)
    request.session['reg_type'] = reg_type
    request.session['user_id'] = user.id
    return(
             redirect('/register-teacher/') if reg_type == "Teacher"
             else redirect('/register-student/')
     )

def extracted_from_register_Teacher(request, user):
    teacher_uuid = str(uuid.uuid4())
    print('User in extracted_from_register_Teacher:', user)
    wallet = Wallet.objects.create(balance=0.00)
    data = request.POST
    min_hourly_Rate = data['min_hourly_rate']
    max_hourly_Rate = data['max_hourly_rate']
    sub1 = data['sub1']
    sub2 = data['sub2']
    sub3 = data['sub3']
    exp = data['exp']
    standard_or_semester = request.POST.get('standard') or request.POST.get('semester')
    teacher_type = data['teacher_type']
    gender = data['gender']
    img = request.FILES.get('teacher_image')
    
    print('Min Hourly Rate:', min_hourly_Rate)
    print('Max Hourly Rate:', max_hourly_Rate)
    print('Subject 1:', sub1)
    print('Subject 2:', sub2)
    print('Subject 3:', sub3)
    print('Experience:', exp)
    print('Standard or Semester:', standard_or_semester)
    print('Teacher Type:', teacher_type)
    print('Gender:', gender)
    print('Teacher Image:', img)

    try:
        gender_instance, _ = Gender.objects.get_or_create(gender=gender.title())
        sub_instance_1, _ = Subject.objects.get_or_create(subject=sub1.title())
        sub_instance_2, _ = Subject.objects.get_or_create(subject=sub2.title())
        sub_instance_3, _ = Subject.objects.get_or_create(subject=sub3.title())

        if img is not None:
            teacher = Teacher.objects.create(
                id=teacher_uuid,
                user=user,
                subject1=sub_instance_1,
                subject2=sub_instance_2,
                subject3=sub_instance_3,
                experience=exp,
                gender=gender_instance,
                teacher_image=img,
                min_hourly_rate=min_hourly_Rate,
                max_hourly_rate=max_hourly_Rate,
                wallet=wallet,
                teacher_type=teacher_type,
                standard_or_semester=standard_or_semester
            )
        else:
            teacher = Teacher.objects.create(
                id=teacher_uuid,
                user=user,
                subject1=sub_instance_1,
                subject2=sub_instance_2,
                subject3=sub_instance_3,
                experience=exp,
                gender=gender_instance,
                min_hourly_rate=min_hourly_Rate,
                max_hourly_rate=max_hourly_Rate,
                teacher_type=teacher_type,
                wallet=wallet,
                standard_or_semester=standard_or_semester
            )

        print('Teacher:', teacher)
    except Exception as e:
        print(f'Error creating Teacher: {e}')

    return redirect('home')


def extracted_from_register_student(request, user):
     print('User:', user)
     student_uuid = str(uuid.uuid4())
     try:
        print("Received request to register a student.")
        wallet = Wallet.objects.create(balance=0.00)
        ins_type = request.POST.get('ins_type', '')
        standard_or_semester = request.POST.get('standard') or request.POST.get('semester', '')
        institution_name = request.POST.get('institution_name', '')
        gender = request.POST.get('gender', '')
        img = request.FILES.get('student_image')
        print(f"Received data - ins_type: {ins_type}, standard_or_semester: {standard_or_semester}, institution_name: {institution_name}, gender: {gender}")
        gender_instance, _ = Gender.objects.get_or_create(gender=gender.title())
        if img is not None:
            print("Creating student with image.")
            student = Student.objects.create(
                id=student_uuid,
                user=user,
                institution_type=ins_type,
                standard_or_semester=standard_or_semester,
                institution_name=institution_name,
                gender=gender_instance,
                student_image=img,
                wallet=wallet
            )
        else:
            print("Creating student without image.")
            student = Student.objects.create(
                id=student_uuid,
                user=user,
                institution_type=ins_type,
                standard_or_semester=standard_or_semester,
                institution_name=institution_name,
                gender=gender_instance,
                wallet=wallet
            )

    
        print(f"Student created - ID: {student.id}, User: {student.user}, Institution Type: {student.institution_type}, Standard/Semester: {student.standard_or_semester}, Institution Name: {student.institution_name}, Gender: {student.gender}, Wallet: {student.wallet}")
        return redirect('home')
     except Exception as e:
        print(f"An error occurred: {e}")
        return print(f"An error occurred: {e}")
   
@never_cache
@login_required(login_url='home')
def book_session(request, teacher_id):
    try:
        student = Student.objects.get(user=request.user)
        user_type = "student"
    except Student.DoesNotExist:
        user_type = "teacher"
    try:
        teacher = get_object_or_404(Teacher, id=teacher_id)
        month_param = request.GET.get('month', None)
        d = get_date(month_param)
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(request.user, user_type, withyear=True)
        context = {
            'calendar': mark_safe(html_cal),
            'prev_month': prev_month(d),
            'next_month': next_month(d),
            'teacher': teacher,
            'user_type': user_type
        }
        return render(request, 'calendar.html', context)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        messages.error(request, 'An error occurred. Please try again later.')
        return render(request, 'error.html')

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
    if search_query := request.GET.get('search_query'):
        subjects_filter = (Q(subject1__subject__icontains=search_query) | 
                               Q(subject2__subject__icontains=search_query) | 
                               Q(subject3__subject__icontains=search_query))
        username_filter = Q(user__username__icontains=search_query)
        queryset = queryset.filter(subjects_filter | username_filter)
    context = {'teachers': queryset,'student':student}
    paginator = Paginator(queryset, 2) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    context = {'teachers': page_obj,'student':student}
    return render(request, 'teacher_registered_list.html', context)


@never_cache
@login_required(login_url='home')
def event(request, teacher_id, event_id=None):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    instance = get_object_or_404(Event, pk=event_id) if event_id else Event()
    student = None
    try:
        student = Student.objects.get(user=request.user)
        user_type = "student"
    except Student.DoesNotExist:
        user_type = "teacher"
        if request.user != teacher.user:
            return HttpResponseForbidden("Forbidden access!")

  
    form_params = {
        'request': request,
        'user': request.user,
        'user_type': user_type,
        'data': request.POST or None,
        'instance': instance,
        'initial': {'created_by': teacher}
        if student is None
        else {'booked_by': student},
    }

    form = EventForm(**form_params)
    if request.POST and form.is_valid():
        data = request.POST
        start_time=data['start_time']
        end_time=data['end_time']
        print(start_time)
        print(end_time)
        if len(start_time)==0:
            messages.error(request,"Start date cannot be empty")
            return redirect(reverse('event_new', kwargs={'teacher_id': teacher.id}))
        if len(end_time)==0:
            messages.error(request,"end date cannot be empty")
            return redirect(reverse('event_new', kwargs={'teacher_id': teacher.id}))
        if start_time>end_time:
            messages.error(request,"Start date cannot be more than end date")
            return redirect(reverse('event_new', kwargs={'teacher_id': teacher.id}))
        start_date_str = data['start_time'].split('T')[0]  
        start_time_str = data['start_time'].split('T')[1]
        end_date_str = data['end_time'].split('T')[0]  
        end_time_str = data['end_time'].split('T')[1]    
        start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d")
        start_time_obj = datetime.strptime(start_time_str, "%H:%M")
        end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d")
        end_time_obj = datetime.strptime(end_time_str, "%H:%M")
        cost=data['event_cost']
        if int(cost)<0:
            messages.error(request,"Event cost cannot be negative")
            return redirect(reverse('event_new', kwargs={'teacher_id': teacher.id}))
        if Event.objects.filter(Q(start_time__date__gte=start_date_obj,end_time__date__lte=end_date_obj) &
                                (Q(start_time__time__lte=start_time_obj,end_time__time__gte=end_time_obj)|
                                Q(start_time__time__gte=start_time_obj,end_time__time__lte=end_time_obj))).exists():
                print("Not Possible")
                messages.error(request,"Not Possible")
                return redirect(reverse('event_new', kwargs={'teacher_id': teacher.id}))
        form.save()
        return redirect(reverse('book_session', kwargs={'teacher_id': teacher.id}))
    if event_id is None:
        return render(request, 'event.html', {'form': form, 'teacher': teacher, 'user_type': user_type})
    return render(request, 'event.html', {'form': form, 'instance': instance, 'teacher': teacher, 'user_type': user_type})

@never_cache
@login_required(login_url='home')
def available_slots_student(request, teacher_id):
    teacher=get_object_or_404(Teacher,id=teacher_id)
    student=Student.objects.get(user=request.user)
    teacher_events = Event.objects.filter(created_by__id=teacher_id, booked_by__isnull=True)
    if request.method=="POST":
        selected_date = request.POST.get('selectedDate')
        date_filter = Q(start_time__icontains=selected_date)
        teacher_events = teacher_events.filter(date_filter)
    return render(request, 'available_slots.html', {'teacher_events': teacher_events,'teacher':teacher,'student':student})


@never_cache
@login_required(login_url='home')
def booked_slots_students(request):
   student = Student.objects.get(user=request.user)
   booked_events = Event.objects.filter(booked_by__id=student.id)
   context = {
        'booked_events': booked_events,
        'student':student
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
        if event.booked_by is not None and event.created_by is not None:
            teacher = event.created_by
            student = event.booked_by
            event_cost=event.duration*event.event_cost
            print(student.wallet.balance)
            student.wallet.deposit(event_cost)
            print(student.wallet.balance)
            print(teacher.wallet.balance)
            teacher.wallet.withdraw(event_cost)
            print(teacher.wallet.balance)
        event.delete()
        return redirect('/teacher-profile-teacher/')
    context = {'event': event}
    return render(request, 'delete_event.html', context)

@never_cache
def logout_page(request):
   logout(request)
   return redirect('home')

@never_cache
@login_required(login_url='home')
def update_student(request, student_id):
    student = Student.objects.get(id=student_id)
    if request.method == "POST":
        print(request.POST)
        institution_type = request.POST.get("ins_type", "")
        student.institution_type = institution_type if institution_type  else  student.institution_type
        standard_or_semester = request.POST.get("standard", "") or request.POST.get("semester", "")
        print(standard_or_semester)
        student.standard_or_semester = standard_or_semester if standard_or_semester else student.standard_or_semester
        institution_name = request.POST.get("institution_name", "")
        student.institution_name= institution_name  if institution_name  else student.institution_name 
        gender = request.POST.get("gender", "")
        if gender != "":
            gender_instance, _ = Gender.objects.get_or_create(gender=gender.title())
            student.gender = gender_instance 
        img = request.FILES.get('student_image')
        if img is not None:
            print('yay!')
            student.student_image = img
        else:
            print('Nay')
        student.gender_instance, _ = Gender.objects.get_or_create(gender=gender.title())
        student.save()
        return redirect('/student-profile/')
    return render(request, 'student_update.html', {'student': student})

from django.contrib import messages

@never_cache
@login_required(login_url='home')
def update_teacher(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id)
    print(teacher)
    if request.method == "POST":
        data = request.POST
        print(data)
        print(data["min_hourly_rate"])
        print(f"Received POST request for updating teacher {teacher_id}")
        teacher_type = data.get("teacher_type", "")
        teacher.teacher_type = teacher_type if teacher_type else teacher.teacher_type
        print(f"Updated teacher_type to: {teacher.teacher_type}")
        standard_or_semester = request.POST.get("standard", "") or request.POST.get("semester", "")
        teacher.standard_or_semester = standard_or_semester if standard_or_semester else teacher.standard_or_semester
        print(f"Updated standard_or_semester to: {teacher.standard_or_semester}")
        min_hourly_rate_input = data.get("min_hourly_rate", "")
        print(f"min_hourly_rate_input: {min_hourly_rate_input}")
        max_hourly_rate_input = data.get("max_hourly_rate", "")
        print(f"max_hourly_rate_input: {max_hourly_rate_input}")
        if min_hourly_rate_input:
            try:
                min_hourly_rate = int(min_hourly_rate_input)
                teacher.min_hourly_rate = min_hourly_rate
                print(f"Updated min_hourly_Rate to: {teacher.min_hourly_rate}")
            except ValueError as e:
                print(f"Error converting min_hourly_rate to int: {e}")
        else:
            print("No min_hourly_rate provided, keeping the existing value.")
        if max_hourly_rate_input:
            try:
                max_hourly_rate = int(max_hourly_rate_input)
                teacher.max_hourly_rate = max_hourly_rate
                print(f"Updated max_hourly_Rate to: {teacher.max_hourly_rate}")
            except ValueError as e:
                print(f"Error converting max_hourly_rate to int: {e}")
        else:
            print("No min_hourly_rate provided, keeping the existing value.")
        print(f"Updated hourly_Rate to: {teacher.min_hourly_rate} and {teacher.max_hourly_rate}")
        sub1 = data.get("sub1", "")
        if sub1 != "":
            teacher.subject1, _ = Subject.objects.get_or_create(subject=sub1.title())
        sub2 = data.get("sub2", "")
        if sub2 != "":
            teacher.subject2, _ = Subject.objects.get_or_create(subject=sub2.title())
        sub3 = data.get("sub3", "")
        if sub3 != "":
            teacher.subject3, _ = Subject.objects.get_or_create(subject=sub3.title())
        exp = int(data["exp"]) if "exp" in data and data["exp"] != '' else teacher.experience
        teacher.experience = exp
        gender = data.get("gender", "")
        if gender != "":
            gender_instance, _ = Gender.objects.get_or_create(gender=gender.title())
            teacher.gender = gender_instance
        img = request.FILES.get('teacher_image')
        if img is not None:
            teacher.teacher_image = img
            print('Yeah!')
        else:
            print('Nah man!')
        print("Saving changes to the database...")
        teacher.save()
        return redirect('/teacher-profile-teacher/')
    return render(request, 'teacher_update.html', {'teacher': teacher})

@never_cache
@login_required(login_url='home')
def view_wallet(request):
    student=None
    teacher=None
    try:
        student = Student.objects.get(user=request.user)
        user_type = "student"
    except Student.DoesNotExist:
        user_type = "teacher"
        teacher=Teacher.objects.get(user=request.user)
        if request.user != teacher.user:
           return HttpResponseForbidden("Red Alert,Red Alert!")
    if user_type=='student':
       student_wallet = student.wallet
       return render(request, 'view_fake_wallet.html', {'wallet': student_wallet,'user_type':user_type,'student':student})
    else:
       teacher_wallet=teacher.wallet
       return render(request, 'view_fake_wallet_teacher.html', {'wallet': teacher_wallet,'user_type':user_type,'teacher':teacher})

@never_cache
@login_required(login_url='home')
def deposit_money(request):
    student = Student.objects.get(user=request.user)
    current_year = datetime.now().year
    months = [str(i) for i in range(1, 13)]
    years = [str(i)[-2:] for i in range(current_year, current_year + 10)]

    context = {
        'months': months,
        'years': years,
        'student': student
    }

    if request.method == 'POST':
        print(request.POST)
        credit_card = request.POST.get('credit_card')
        # cvv = request.POST.get('cvv')
        expiration_date = request.POST.get('expiration_date')
        if not is_valid_credit_card(credit_card):
            messages.error(request, "Invalid credit card number")
            return redirect(reverse('deposit_money'))
        # if not is_valid_cvv(cvv):
        #     messages.error(request, "Invalid CVV")
        #     return redirect(reverse('deposit_money'))
        if not is_valid_expiration_date(expiration_date):
            messages.error(request, "Invalid expiration date")
            return redirect(reverse('deposit_money'))
        if student.wallet is not None:
            amount = float(request.POST.get('amount'))
            student.wallet.deposit(amount)
        else:
            print("No wallet associated with the student")
        return redirect(reverse('view_wallet'))
    return render(request, 'deposit_fake_money.html', context)

def is_valid_credit_card(credit_card):
    card_number = int(credit_card)
    idx = 0
    total_sum = 0
    while card_number > 0:
        digit = card_number % 10
        if idx%2==1: 
            digit *= 2
            if digit >= 10:
                digit = digit % 10 + digit // 10
        total_sum += digit
        card_number //= 10
        idx += 1
    return bool(total_sum % 10 == 0 and len(credit_card) == 16 and credit_card.isdigit())


# def is_valid_cvv(cvv):
#     return len(cvv) == 3 and cvv.isdigit()

def is_valid_expiration_date(expiration_date):
    if len(expiration_date) != 5:
        return False
    if not expiration_date[:2].isdigit() or not expiration_date[3:].isdigit():
        return False
    month = int(expiration_date[:2])
    year = int(expiration_date[3:])
    if not 1 <= month <= 12:
        return False
    current_year = datetime.now().year % 100
    if year < current_year or (year == current_year and month < datetime.now().month):
        return False
    return True

@never_cache
@login_required(login_url='home')
def book_slot(request, teacher_id, student_id, event_id):
    teacher = Teacher.objects.get(id=teacher_id)
    student = Student.objects.get(id=student_id)
    event = Event.objects.get(id=event_id)
    event_cost = event.duration * event.event_cost
    if student.wallet.balance >= event_cost:
        student.wallet.withdraw(event_cost)
        teacher.wallet.deposit(event_cost)
        event.booked_by = student
        event.save()
        return render(request, 'booking_success.html', {'teacher': teacher, 'event': event})
    else:
        return HttpResponse("Plz Fill your Balance")


@never_cache
@login_required(login_url='home')
def request_session(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    student= Student.objects.get(user=request.user)
    print(teacher)
    if request.method == 'POST':
        form = SessionRequestForm(request.POST)
        if form.is_valid():
            cost=form.cleaned_data['requested_cost']
            start_time=form.cleaned_data['start_time']
            end_time=form.cleaned_data['end_time']
            print(start_time)
            print(end_time)
            print(start_time.date())
            print(end_time.date())
            print(start_time.time())
            print(end_time.time())
            if start_time is None:
                messages.error(request,"Start date cannot be empty")
                return redirect(reverse('request_session', kwargs={'teacher_id': teacher.id}))
            if end_time is None:
                messages.error(request,"end date cannot be empty")
                return redirect(reverse('request_session', kwargs={'teacher_id': teacher.id}))
            if start_time>end_time:
                messages.error(request,"Start date cannot be more than end date")
                return redirect(reverse('request_session', kwargs={'teacher_id': teacher.id}))
            if cost<0:
                messages.error(request,"Negative Cost")
                return redirect(reverse('request_session', kwargs={'teacher_id': teacher.id}))
            if student.wallet.balance-cost<=0:
                messages.error(request,"Plz refill your wallet balance")
                return redirect(reverse('request_session', kwargs={'teacher_id': teacher.id}))
            # filtered_sessions=SessionRequest.objects.filter(Q(start_time__date__gte=start_time.date(),end_time__date__lte=end_time.date()) &
            #                     (Q(start_time__time__lte=start_time.time(),end_time__time__gte=end_time.time())|
            #                     Q(start_time__time__gte=start_time.time(),end_time__time__lte=end_time.time())))
            # values_list = filtered_sessions.values()
            # for session_values in values_list:
            #     print(session_values)
            if SessionRequest.objects.filter(Q(start_time__date__gte=start_time.date(),end_time__date__lte=end_time.date()) &
                                (Q(start_time__time__lte=start_time.time(),end_time__time__gte=end_time.time())|
                                Q(start_time__time__gte=start_time.time(),end_time__time__lte=end_time.time()))).exists():
                print("Not Possible")
                messages.error(request,"Already a session exist")
                return redirect(reverse('request_session', kwargs={'teacher_id': teacher.id}))
            session_request = form.save(commit=False)
            session_request.student = student
            session_request.teacher = teacher
            session_request.save()
            return redirect(reverse('teacher_profile', kwargs={'teacher_id': teacher.id}))
    else:
        # print(teacher.title_choices)
        initial_data = {
            'instance': teacher,
        }
        form = SessionRequestForm(**initial_data)
    return render(request, 'request_session.html', {'form': form, 'teacher': teacher,'student':student})

@never_cache
@login_required(login_url='home')
def view_session_requests(request):
    teacher = Teacher.objects.get(user=request.user)
    session_requests = SessionRequest.objects.filter(teacher=teacher)
    print(session_requests)
    return render(request, 'view_session_requests.html', {'session_requests': session_requests,'teacher':teacher})

@never_cache
@login_required(login_url='home')
def approve_session_requests(request,session_id):
    session=SessionRequest.objects.get(id=session_id)
    event=Event.objects.create(created_by=session.teacher,booked_by=session.student,start_time=session.start_time,end_time=session.end_time,description=session.message,title=session.title,event_cost=session.requested_cost)
    teacher=event.created_by
    student=event.booked_by
    event_cost = event.duration * event.event_cost
    if student.wallet.balance>=event_cost:
        print(student.wallet.balance)
        student.wallet.withdraw(event_cost)
        print(student.wallet.balance)
        print(teacher.wallet.balance)
        teacher.wallet.deposit(event_cost)
        print(teacher.wallet.balance)
        session.delete()
        return redirect('/booked-slots-teacher/')
    else:
        event.delete()
        return HttpResponse("Student does not have enough balance")


@never_cache
@login_required(login_url='home')
def requested_sessions(request):
    student=Student.objects.get(user=request.user)
    sessions=SessionRequest.objects.filter(student=student)
    return render(request, 'view_session_requests_student.html', {'session_requests': sessions,'student':student})


@never_cache
@login_required(login_url='home')
def delete_request(request,session_id):
    session=SessionRequest.objects.filter(id=session_id)
    session.delete()
    return redirect('/view-session-requests/')

