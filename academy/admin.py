from django.contrib import admin
from .models import Student, Staff, Attendance, LeaveRequest, Result, Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'class_name', 'total_marks')
    list_filter = ('course', 'class_name')
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'course', 'enrollment_date', 'attendance_score')
    search_fields = ('student_id', 'name', 'contact_number')
    list_filter = ('course',)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'role', 'contact_number')
    search_fields = ('staff_id', 'name')
    list_filter = ('role',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'sms_sent')
    list_filter = ('date', 'status', 'sms_sent')
    search_fields = ('student__name', 'student__student_id')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('student__name', 'student__student_id')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'year', 'exam_type', 'overall_grade', 'percentage')
    list_filter = ('year', 'exam_type', 'overall_grade')
    search_fields = ('student__name', 'student__student_id')
