"""
URL configuration for tut project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home.views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home,name="home"),
    path("register/",register,name="register"),
    path("register-teacher/",register_teacher,name="register_teacher"),
    path("register-student/",register_student,name="register_student"),
    path("teachers-list/",teachers_list,name="teachers_list"),
    path("teacher-profile/<teacher_id>",teacher_profile,name="teacher_profile"),
    path("student-profile/",student_profile,name="student_profile"),
    path("add-feedback/<teacher_id>",add_feedback,name="add_feedback")
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
