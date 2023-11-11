from django.contrib import admin
from django.urls import path, include
from home.views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("register-teacher/", register_teacher, name="register_teacher"),
    path("register-student/", register_student, name="register_student"),
    path("teachers-list/", teachers_list, name="teachers_list"),
    path("teacher-profile/<teacher_id>", teacher_profile, name="teacher_profile"),
    path("student-profile/", student_profile, name="student_profile"),
    path("add-feedback/<teacher_id>", add_feedback, name="add_feedback"),
    path("book-session/<teacher_id>", book_session, name="book_session"),
    path("register-under-teacher/<teacher_id>", register_under_teacher, name="register_under_teacher"),
    path("registered-teachers-list/",registered_teachers_list,name="registered_teachers_list"),
    path('event/new/<teacher_id>',event, name='event_new'),
    path('event-edit/<teacher_id>/<int:event_id>',event,name='event_edit'),
    path('available-slot-student/<teacher_id>/',available_slots_student,name='available_slots_student'),
    path('booked-slots-students/',booked_slots_students,name="booked_slots_students"),
    #Teacher-related-shit
    path('teacher-profile-teacher/',teacher_profile_teacher,name='teacher_profile_teacher'),
    path('registered-students/',registered_students_teacher,name='registered_students_teacher'),
    path('student-profile-teacher/<int:student_id>',student_profile_teacher,name='student_profile_teacher'),
    path('available-slot-teacher/',available_slot_teacher,name='available_slot_teacher'),
    path('booked-slots-teacher/',booked_slots_teacher,name='booked_slots_teacher'),
    path('delete-event/<int:event_id>/',delete_event, name='delete_event'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

