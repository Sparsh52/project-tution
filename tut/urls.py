from django.contrib import admin
from django.urls import path, include
from home.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



# handler404 = handler404

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
    path('event-edit/<teacher_id>/<event_id>',event,name='event_edit'),
    path('available-slot-student/<teacher_id>/',available_slots_student,name='available_slots_student'),
    path('booked-slots-students/',booked_slots_students,name="booked_slots_students"),
     path('update-student/<student_id>/', update_student, name='student_update'),
    #Teacher-related-stuff
    path('teacher-profile-teacher/',teacher_profile_teacher,name='teacher_profile_teacher'),
    path('registered-students/',registered_students_teacher,name='registered_students_teacher'),
    path('student-profile-teacher/<student_id>',student_profile_teacher,name='student_profile_teacher'),
    path('available-slot-teacher/',available_slot_teacher,name='available_slot_teacher'),
    path('booked-slots-teacher/',booked_slots_teacher,name='booked_slots_teacher'),
    path('delete-event/<event_id>/',delete_event, name='delete_event'),
    path('update-teacher/<teacher_id>',update_teacher,name="teacher_update"),
    path('logout/',logout_page, name='logout'),
    path('view-wallet/', view_wallet, name='view_wallet'),
    path('deposit-money/', deposit_money, name='deposit_money'),
    path('book-slot/<teacher_id>/<student_id>/<event_id>/', book_slot, name='book_slot'),
    path('request-session/<teacher_id>/', request_session, name='request_session'),
    path('view-session-requests/', view_session_requests, name='view_session_requests'),
    path('approve-session-requests/<session_id>', approve_session_requests, name='approve_session_requests'),
    path('requested-sessions/', requested_sessions, name='requested_sessions'),
    path('delete-request/<session_id>', delete_request, name='delete_request'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset_form.html"), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
    path('reset-session/<session_id>', reset_session_view, name='reset_session_view'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

