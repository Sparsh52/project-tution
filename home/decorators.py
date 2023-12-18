import contextlib
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
                student = Student.objects.get(user=request.user)
                if next_page is not None and next_page!='http://127.0.0.1:8000/':
                    return redirect(next_page)
                else:
                    return redirect('/student-profile/')
        return view_func(request, *args, **kwargs)
    return wrapper
