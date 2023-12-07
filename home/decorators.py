from .models import Teacher, Student
from django.shortcuts import render, redirect
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def logindec(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        next_page = request.GET.get('next', request.META.get('HTTP_REFERER'))
        if request.user.is_authenticated:
            try:
                teacher = Teacher.objects.get(user=request.user)
                if teacher and next_page:
                    print(f"In Teacher {teacher}")
                    return redirect(next_page)
                else:
                    return redirect('/teacher-profile-teacher/')
            except Teacher.DoesNotExist:
                try:
                    student = Student.objects.get(user=request.user)
                    if student and next_page:
                        print(f"In Student {student}")
                        return redirect(next_page)
                    else:
                        return redirect('/student-profile/')
                except Student.DoesNotExist:
                    messages.error(request, 'You are not a registered user.')
                    return redirect('/')
        return view_func(request, *args, **kwargs)

    return wrapper
