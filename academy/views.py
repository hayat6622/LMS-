from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Staff, Attendance, LeaveRequest, Result, Subject
from .forms import AdmissionForm, SubjectForm
from django.db.models import Sum, Q

def dashboard(request):
    students = Student.objects.all()
    staff = Staff.objects.all()
    pending_leaves = LeaveRequest.objects.filter(status='Pending').count()
    
    total_sahib = students.filter(is_sahib_tarteeb=True).count()
    
    context = {
        'total_students': students.count(),
        'total_staff': staff.count(),
        'pending_leaves': pending_leaves,
        'total_sahib': total_sahib,
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
        all_students = all_students.filter(
            Q(name__icontains=query) | 
            Q(name_en__icontains=query) | 
            Q(student_id__icontains=query)
        )
        
    course_filter = request.GET.get('course', 'All')
    sahib_filter = request.GET.get('is_sahib_tarteeb', '')
    
    if sahib_filter == 'true':
        all_students = all_students.filter(is_sahib_tarteeb=True)
    
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
        'sahib_filter': sahib_filter,
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

    results = student.results.all().order_by('-year', 'exam_type')

    context = {
        'student': student,
        'attendance_records': attendance_records[:30],  # Latest 30 records
        'results': results,
        'summary': {
            'total': total_days,
            'present': present_days,
            'absent': absent_days,
            'leave': leave_days,
            'percentage': round(attendance_percentage, 1),
            'total_late_minutes': student.total_late_minutes_last_year(),
            'no_absences': student.no_absences_last_year()
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
            minutes_late = request.POST.get(f'minutes_late_{student.student_id}', 0)
            if not str(minutes_late).isdigit():
                minutes_late = 0
            
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': status, 'minutes_late': int(minutes_late)}
                )
                
                # Check if student should be removed from Sahib Tarteeb
                # 1. "if the student is absent he will be remove rom this list"
                # 2. "if the students is late 60 minutes in last year remove him rom sahib tarteeb"
                if student.is_sahib_tarteeb:
                    if status == 'Absent':
                        student.is_sahib_tarteeb = False
                        student.save()
                    else:
                        total_late = student.total_late_minutes_last_year()
                        if total_late >= 60:
                            student.is_sahib_tarteeb = False
                            student.save()

        messages.success(request, f"حاضری کامیابی سے محفوظ ہو گئی۔ / Attendance for {attendance_date} saved successfully.")
        return redirect(f"{request.path}?date={date_str}&course={course_filter}&desired_class={class_filter}")

    # Get existing attendance for the selected date to prepopulate
    existing_attendance = Attendance.objects.filter(date=attendance_date, student__in=students)
    attendance_map = {att.student_id: {'status': att.status, 'minutes_late': att.minutes_late} for att in existing_attendance}
    
    # Add properties to student objects for the template
    for student in students:
        att_data = attendance_map.get(student.student_id, {'status': 'Present', 'minutes_late': 0})
        student.current_status = att_data['status']
        student.current_minutes_late = att_data['minutes_late']

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
    exam_type = request.GET.get('exam_type', 'سالانہ امتحان')

    students = []
    subjects = []
    
    if course and class_name:
        students = Student.objects.filter(course=course, desired_class=class_name)
        if course == 'شعبہ کتب':
            subjects = Subject.objects.filter(course=course, class_name=class_name)
        else:
            # For other courses, subjects are the same for all classes
            subjects = Subject.objects.filter(course=course)

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
                    exam_type=exam_type,
                    defaults={'subjects_json': subjects_data}
                )
                if not created:
                    result.subjects_json = subjects_data
                    result.save()
            
            messages.success(request, "Results saved successfully.")
            return redirect(f"{request.path}?course={course}&class_name={class_name}&year={year}&exam_type={exam_type}")
        except Exception as e:
            messages.error(request, f"Error saving results: {e}")

    # For the form, we need current results if any
    current_results = {}
    if students:
        results = Result.objects.filter(student__in=students, year=year, exam_type=exam_type)
        for r in results:
            current_results[r.student.student_id] = r.subjects_json

    return render(request, 'academy/result_entry.html', {
        'students': students,
        'subjects': subjects,
        'current_results': current_results,
        'course': course,
        'class_name': class_name,
        'year': year,
        'exam_type': exam_type,
        'course_choices': Student.COURSE_CHOICES,
        'class_choices': Student.KUTUB_CLASS_CHOICES + Student.GENERAL_CLASS_CHOICES,
        'kutub_classes': Student.KUTUB_CLASS_CHOICES,
        'general_classes': Student.GENERAL_CLASS_CHOICES,
        'exam_type_choices': Result.EXAM_TYPE_CHOICES,
    })

def student_result_card(request, student_id, year, exam_type):
    student = get_object_or_404(Student, student_id=student_id)
    # We might need to handle URL encoding if exam_type is passed in URL
    result = get_object_or_404(Result, student=student, year=year, exam_type=exam_type)
    return render(request, 'academy/result_card.html', {
        'student': student,
        'result': result,
        'subjects': result.subjects_json
    })

def class_gazette(request):
    course = request.GET.get('course')
    class_name = request.GET.get('class_name')
    year = request.GET.get('year', '2024')
    exam_type = request.GET.get('exam_type', 'سالانہ امتحان')

    results = []
    subjects_list = []
    
    if course and class_name:
        # Get all results for this class
        results_qs = Result.objects.filter(
            student__course=course,
            student__desired_class=class_name,
            year=year,
            exam_type=exam_type
        ).select_related('student').order_by('-obtained_marks')
        
        # Determine all subjects involved
        all_subjects = set()
        for r in results_qs:
            for sub_name in r.subjects_json.keys():
                all_subjects.add(sub_name)
        
        subjects_list = sorted(list(all_subjects))
        
        # Ranking logic
        current_rank = 0
        last_marks = -1
        for i, r in enumerate(results_qs):
            if r.obtained_marks != last_marks:
                current_rank = i + 1
            r.position = current_rank
            last_marks = r.obtained_marks
            
            # Helper for template to access marks by subject name
            r.marks_list = [r.subjects_json.get(s, '-') for s in subjects_list]
            results.append(r)

    return render(request, 'academy/class_gazette.html', {
        'results': results,
        'subjects': subjects_list,
        'course': course,
        'class_name': class_name,
        'year': year,
        'exam_type': exam_type,
        'course_choices': Student.COURSE_CHOICES,
        'class_choices': Student.KUTUB_CLASS_CHOICES + Student.GENERAL_CLASS_CHOICES,
        'exam_type_choices': Result.EXAM_TYPE_CHOICES,
    })

def student_transcript(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    results = student.results.all().order_by('year', 'exam_type')
    
    # Calculate overall career summary
    total_obtained = sum(r.obtained_marks for r in results)
    total_possible = sum(r.total_marks for r in results)
    overall_percentage = (total_obtained / total_possible * 100) if total_possible > 0 else 0
    
    return render(request, 'academy/transcript.html', {
        'student': student,
        'results': results,
        'summary': {
            'total_obtained': total_obtained,
            'total_possible': total_possible,
            'percentage': round(overall_percentage, 1)
        }
    })

