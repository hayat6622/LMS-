from django.urls import path
from . import views

app_name = 'academy'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admission/', views.admission, name='admission'),
    path('admission/receipt/<str:student_id>/', views.admission_receipt, name='admission_receipt'),
    path('directory/', views.directory, name='directory'),
    path('directory/<str:student_id>/', views.student_profile, name='student_profile'),
    path('directory/<str:student_id>/edit/', views.student_edit, name='student_edit'),
    path('subjects/', views.subjects_manage, name='subjects_manage'),
    path('results/entry/', views.result_bulk_entry, name='result_bulk_entry'),
    path('results/card/<str:student_id>/<str:year>/<str:exam_type>/', views.student_result_card, name='student_result_card'),
    path('attendance/', views.attendance, name='attendance'),
    path('staff/', views.staff_management, name='staff_management'),
    path('staff/add/', views.staff_create, name='staff_create'),
    path('leaves/', views.leave_management, name='leave_management'),
    path('results/gazette/', views.class_gazette, name='class_gazette'),
    path('directory/<str:student_id>/transcript/', views.student_transcript, name='student_transcript'),
]
