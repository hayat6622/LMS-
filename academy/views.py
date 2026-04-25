from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Staff, Attendance, LeaveRequest, Result, Subject
from .forms import AdmissionForm, SubjectForm

def dashboard(request):
    students = Student.objects.all()
    staff = Staff.objects.all()
    pending_leaves = LeaveRequest.objects.filter(status='Pending').count()
    context = {
        'total_students': students.count(),
        'total_staff': staff.count(),
        'pending_leaves': pending_leaves,
    }
    return render(request, 'academy/dashboard.html', context)

def admission(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"طالب علم {student.name} کامیابی سے داخل ہو گیا۔ / Successfully enrolled scholar {student.name}.")
            return redirect('academy:admission_receipt', student_id=student.student_id)
        else:
            messages.error(request, "براہ کرم نیچے دی گئی غلطیاں درست کریں۔ / Please correct the errors below.")
    else:
        form = AdmissionForm()
        
    return render(request, 'academy/admission.html', {'form': form})

def student_edit(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        form = AdmissionForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"طالب علم {student.name} کی معلومات کامیابی سے اپ ڈیٹ ہو گئیں۔ / Student {student.name} updated successfully.")
            return redirect('academy:student_profile', student_id=student.student_id)
        else:
            messages.error(request, "براہ کرم نیچے دی گئی غلطیاں درست کریں۔ / Please correct the errors below.")
    else:
        form = AdmissionForm(instance=student)
        
    return render(request, 'academy/student_edit.html', {'form': form, 'student': student})

def admission_receipt(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    return render(request, 'academy/receipt.html', {'student': student})

def directory(request):
    all_students = Student.objects.all()
    
    query = request.GET.get('q', '')
    if query:
        all_students = all_students.filter(name__icontains=query) | all_students.filter(student_id__icontains=query)
        
    course_filter = request.GET.get('course', 'All')
    
    total_count = all_students.count()
    hifz_count = all_students.filter(course='شعبہ حفظ و ناظرہ').count()
    alim_count = all_students.filter(course='شعبہ کتب').count()
    basic_count = all_students.filter(course='شعبہ بنین').count()
    
    students = all_students
    if course_filter and course_filter != 'All':
        students = students.filter(course=course_filter)
        
    context = {
        'students': students,
        'query': query,
        'course_filter': course_filter,
        'total_count': total_count,
        'hifz_count': hifz_count,
        'alim_count': alim_count,
        'basic_count': basic_count,
    }
    return render(request, 'academy/directory.html', context)

def student_profile(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    attendance_records = student.attendances.all().order_by('-date')
    
    # Calculate summary
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='Present').count()
    absent_days = attendance_records.filter(status='Absent').count()
    leave_days = attendance_records.filter(status='Leave').count()
    
    attendance_percentage = 0
    if total_days > 0:
        attendance_percentage = (present_days / total_days) * 100
    
    # Update student score if it changed significantly (just for sync)
    student.attendance_score = round(attendance_percentage, 1)
    student.save()

    context = {
        'student': student,
        'attendance_records': attendance_records[:30],  # Latest 30 records
        'summary': {
            'total': total_days,
            'present': present_days,
            'absent': absent_days,
            'leave': leave_days,
            'percentage': round(attendance_percentage, 1)
        }
    }
    return render(request, 'academy/profile.html', context)

def attendance(request):
    import datetime
    date_str = request.GET.get('date', datetime.date.today().isoformat())
    try:
        attendance_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        attendance_date = datetime.date.today()
    
    course_filter = request.GET.get('course', 'All')
    class_filter = request.GET.get('desired_class', '')
    
    students = Student.objects.all()
    if course_filter != 'All':
        students = students.filter(course=course_filter)
    if class_filter:
        students = students.filter(desired_class=class_filter)
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.student_id}')
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': status}
                )
        messages.success(request, f"حاضری کامیابی سے محفوظ ہو گئی۔ / Attendance for {attendance_date} saved successfully.")
        return redirect(f"{request.path}?date={date_str}&course={course_filter}&desired_class={class_filter}")

    # Get existing attendance for the selected date to prepopulate
    existing_attendance = Attendance.objects.filter(date=attendance_date, student__in=students)
    attendance_map = {att.student_id: att.status for att in existing_attendance}
    
    # Add a property to student objects for the template
    for student in students:
        student.current_status = attendance_map.get(student.student_id, 'Present')

    # Get departments and unique classes for filters
    departments = [choice[0] for choice in Student.COURSE_CHOICES]
    unique_classes = Student.objects.exclude(desired_class='').values_list('desired_class', flat=True).distinct()

    context = {
        'students': students,
        'date': date_str,
        'attendance_date': attendance_date,
        'course_filter': course_filter,
        'class_filter': class_filter,
        'departments': departments,
        'unique_classes': unique_classes,
    }
    return render(request, 'academy/attendance.html', context)

def staff_management(request):
    staff = Staff.objects.all()
    return render(request, 'academy/staff.html', {'staff': staff})

def staff_create(request):
    from .forms import StaffForm
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"نیا عملہ رکن {member.name} بنایا گیا۔ / New staff member {member.name} created.")
            return redirect('academy:staff_management')
        else:
            messages.error(request, "براہ کرم نیچے دی گئی غلطیاں درست کریں۔ / Please correct the errors below.")
    else:
        form = StaffForm()
    return render(request, 'academy/staff_form.html', {'form': form})

def leave_management(request):
    leaves = LeaveRequest.objects.all().order_by('-start_date')
    return render(request, 'academy/leaves.html', {'leaves': leaves})

def subjects_manage(request):
    subjects = Subject.objects.all().order_by('course', 'class_name')
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject added successfully.")
            return redirect('academy:subjects_manage')
    else:
        form = SubjectForm()
    
    return render(request, 'academy/manage_subjects.html', {
        'subjects': subjects,
        'form': form
    })

def result_bulk_entry(request):
    course = request.GET.get('course')
    class_name = request.GET.get('class_name')
    year = request.GET.get('year', '2024')

    students = []
    subjects = []
    
    # Classes are optional for Hifz and Baneen
    is_class_optional = course in ['شعبہ حفظ و ناظرہ', 'شعبہ بنین']
    
    if course and (class_name or is_class_optional):
        if is_class_optional:
            students = Student.objects.filter(course=course)
            subjects = Subject.objects.filter(course=course)
        else:
            students = Student.objects.filter(course=course, desired_class=class_name)
            subjects = Subject.objects.filter(course=course, class_name=class_name)

    if request.method == 'POST':
        # Process bulk submission
        try:
            for student in students:
                subjects_data = {}
                for subject in subjects:
                    field_name = f"marks_{student.student_id}_{subject.id}"
                    marks = request.POST.get(field_name, 0)
                    subjects_data[subject.name] = marks
                
                result, created = Result.objects.get_or_create(
                    student=student,
                    year=year,
                    defaults={'subjects_json': subjects_data}
                )
                if not created:
                    result.subjects_json = subjects_data
                    result.save()
            
            messages.success(request, "Results saved successfully.")
            return redirect(f"{request.path}?course={course}&class_name={class_name}&year={year}")
        except Exception as e:
            messages.error(request, f"Error saving results: {e}")

    # For the form, we need current results if any
    current_results = {}
    if students:
        results = Result.objects.filter(student__in=students, year=year)
        for r in results:
            current_results[r.student.student_id] = r.subjects_json

    return render(request, 'academy/result_entry.html', {
        'students': students,
        'subjects': subjects,
        'current_results': current_results,
        'course': course,
        'class_name': class_name,
        'year': year,
        'course_choices': Student.COURSE_CHOICES,
        'class_choices': Student.KUTUB_CLASS_CHOICES,
    })

def student_result_card(request, student_id, year):
    student = get_object_or_404(Student, student_id=student_id)
    result = get_object_or_404(Result, student=student, year=year)
    return render(request, 'academy/result_card.html', {
        'student': student,
        'result': result,
        'subjects': result.subjects_json
    })
