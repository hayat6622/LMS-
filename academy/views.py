from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, Staff, Attendance, LeaveRequest, Result, Subject
from .forms import AdmissionForm, SubjectForm
from django.db.models import Sum, Q
from . import firebase_utils

def dashboard(request):
    # Fetch from Firestore instead of SQLite
    students = firebase_utils.list_documents('students')
    staff = firebase_utils.list_documents('staff')
    
    # Example of filtering in Firestore (manual for now, or using queries)
    # For count, we can just take length of list or use Firestore count queries
    total_students = len(students)
    total_staff = len(staff)
    
    # Fetch pending leaves
    leaves_ref = firebase_utils.get_collection('leave_requests')
    pending_leaves_count = len([d for d in firebase_utils.list_documents('leave_requests') if d.get('status') == 'Pending'])
    
    total_sahib = len([s for s in students if s.get('is_sahib_tarteeb')])
    
    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'pending_leaves': pending_leaves_count,
        'total_sahib': total_sahib,
    }
    return render(request, 'academy/dashboard.html', context)

def admission(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            # Get data from form but don't save to SQLite
            data = form.cleaned_data
            
            # Manually handle student_id generation for Firestore
            import datetime
            current_year = datetime.datetime.now().year
            students = firebase_utils.list_documents('students')
            last_id_num = 0
            for s in students:
                sid = s.get('student_id', '')
                if sid.startswith(f'IA-{current_year}-'):
                    try:
                        num = int(sid.split('-')[-1])
                        if num > last_id_num: last_id_num = num
                    except: pass
            
            new_id = f'IA-{current_year}-{(last_id_num + 1):04d}'
            data['student_id'] = new_id
            
            # Convert dates to strings for JSON serialization
            for key, value in data.items():
                if isinstance(value, datetime.date):
                    data[key] = str(value)
                elif hasattr(value, 'staff_id'): # Handle potential Staff object if any
                    data[key] = value.staff_id
            
            # Save to Firestore
            firebase_utils.save_document('students', new_id, data)
            
            messages.success(request, f"طالب علم {data['name']} کامیابی سے داخل ہو گیا۔ / Successfully enrolled scholar {data['name']}.")
            return redirect('academy:admission_receipt', student_id=new_id)
        else:
            messages.error(request, "براہ کرم نیچے دی گئی غلطیاں درست کریں۔ / Please correct the errors below.")
    else:
        form = AdmissionForm()
        
    return render(request, 'academy/admission.html', {'form': form})

def student_edit(request, student_id):
    student_data = firebase_utils.get_document('students', student_id)
    if not student_data:
        return redirect('academy:directory')
        
    if request.method == 'POST':
        form = AdmissionForm(request.POST, initial=student_data)
        if form.is_valid():
            data = form.cleaned_data
            import datetime
            for key, value in data.items():
                if isinstance(value, datetime.date):
                    data[key] = str(value)
            
            firebase_utils.save_document('students', student_id, data)
            messages.success(request, f"Student {data['name']} updated successfully.")
            return redirect('academy:student_profile', student_id=student_id)
    else:
        form = AdmissionForm(initial=student_data)
        
    return render(request, 'academy/student_edit.html', {'form': form, 'student': student_data})

def admission_receipt(request, student_id):
    student = firebase_utils.get_document('students', student_id)
    if not student:
        return redirect('academy:admission')
    return render(request, 'academy/receipt.html', {'student': student})

def directory(request):
    all_students = firebase_utils.list_documents('students')
    
    query = request.GET.get('q', '').lower()
    if query:
        all_students = [
            s for s in all_students 
            if query in s.get('name', '').lower() or 
               query in s.get('name_en', '').lower() or 
               query in s.get('student_id', '').lower()
        ]
        
    course_filter = request.GET.get('course', 'All')
    sahib_filter = request.GET.get('is_sahib_tarteeb', '')
    
    if sahib_filter == 'true':
        all_students = [s for s in all_students if s.get('is_sahib_tarteeb')]
    
    if course_filter and course_filter != 'All':
        all_students = [s for s in all_students if s.get('course') == course_filter]

    total_count = len(all_students)
    hifz_count = len([s for s in all_students if s.get('course') == 'شعبہ حفظ و ناظرہ'])
    alim_count = len([s for s in all_students if s.get('course') == 'شعبہ کتب'])
    basic_count = len([s for s in all_students if s.get('course') == 'شعبہ بنین'])
    
    context = {
        'students': all_students,
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
    student = firebase_utils.get_document('students', student_id)
    if not student:
        return redirect('academy:directory')
        
    all_att = firebase_utils.list_documents('attendance')
    attendance_records = [a for a in all_att if a.get('student_id') == student_id]
    attendance_records = sorted(attendance_records, key=lambda x: x.get('date', ''), reverse=True)
    
    # Calculate summary
    total_days = len(attendance_records)
    present_days = len([a for a in attendance_records if a.get('status') == 'Present'])
    absent_days = len([a for a in attendance_records if a.get('status') == 'Absent'])
    leave_days = len([a for a in attendance_records if a.get('status') == 'Leave'])
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Sync score back to Firestore if needed
    if student.get('attendance_score') != round(attendance_percentage, 1):
        firebase_utils.save_document('students', student_id, {'attendance_score': round(attendance_percentage, 1)})

    all_res = firebase_utils.list_documents('results')
    results = [r for r in all_res if r.get('student_id') == student_id]
    results = sorted(results, key=lambda x: (x.get('year', ''), x.get('exam_type', '')), reverse=True)

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
            'total_late_minutes': sum([int(a.get('minutes_late', 0)) for a in attendance_records]),
            'no_absences': not any([a for a in attendance_records if a.get('status') == 'Absent'])
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
    
    # Fetch students from Firestore
    students = firebase_utils.list_documents('students')
    if course_filter != 'All':
        students = [s for s in students if s.get('course') == course_filter]
    if class_filter:
        students = [s for s in students if s.get('desired_class') == class_filter]
    
    if request.method == 'POST':
        for student in students:
            sid = student.get('student_id')
            status = request.POST.get(f'status_{sid}')
            minutes_late = request.POST.get(f'minutes_late_{sid}', 0)
            if not str(minutes_late).isdigit():
                minutes_late = 0
            
            if status:
                # Save attendance to Firestore
                att_id = f"{sid}_{date_str}"
                att_data = {
                    'student_id': sid,
                    'date': date_str,
                    'status': status,
                    'minutes_late': int(minutes_late)
                }
                firebase_utils.save_document('attendance', att_id, att_data)
                
                # Handle Sahib Tarteeb logic in Firestore
                if student.get('is_sahib_tarteeb'):
                    if status == 'Absent':
                        firebase_utils.save_document('students', sid, {'is_sahib_tarteeb': False})

        messages.success(request, f"حاضری کامیابی سے محفوظ ہو گئی۔ / Attendance for {attendance_date} saved successfully.")
        return redirect(f"{request.path}?date={date_str}&course={course_filter}&desired_class={class_filter}")

    # Get existing attendance from Firestore
    all_att = firebase_utils.list_documents('attendance')
    attendance_map = {a['student_id']: a for a in all_att if a.get('date') == date_str}
    
    # Add properties to student objects for the template
    for student in students:
        att_data = attendance_map.get(student.get('student_id'), {'status': 'Present', 'minutes_late': 0})
        student['current_status'] = att_data['status']
        student['current_minutes_late'] = att_data['minutes_late']

    # Get unique classes for filters
    all_students = firebase_utils.list_documents('students')
    unique_classes = sorted(list(set([s.get('desired_class') for s in all_students if s.get('desired_class')])))
    departments = [choice[0] for choice in Student.COURSE_CHOICES]

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
    staff = firebase_utils.list_documents('staff')
    return render(request, 'academy/staff.html', {'staff': staff})

def staff_create(request):
    from .forms import StaffForm
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            sid = data.get('staff_id')
            
            # Save to Firestore
            firebase_utils.save_document('staff', sid, data)
            
            messages.success(request, f"نیا عملہ رکن {data['name']} بنایا گیا۔ / New staff member {data['name']} created.")
            return redirect('academy:staff_management')
        else:
            messages.error(request, "براہ کرم نیچے دی گئی غلطیاں درست کریں۔ / Please correct the errors below.")
    else:
        form = StaffForm()
    return render(request, 'academy/staff_form.html', {'form': form})

def leave_management(request):
    leaves = firebase_utils.list_documents('leaves')
    leaves = sorted(leaves, key=lambda x: x.get('start_date', ''), reverse=True)
    return render(request, 'academy/leaves.html', {'leaves': leaves})

def subjects_manage(request):
    subjects = firebase_utils.list_documents('subjects')
    # Sort subjects for display
    subjects = sorted(subjects, key=lambda x: (x.get('course', ''), x.get('class_name', '')))
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Generate a simple ID for subject
            import uuid
            sub_id = str(uuid.uuid4())[:8]
            
            # Save to Firestore
            firebase_utils.save_document('subjects', sub_id, data)
            
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
        all_students = firebase_utils.list_documents('students')
        students = [s for s in all_students if s.get('course') == course and s.get('desired_class') == class_name]
        
        all_subjects = firebase_utils.list_documents('subjects')
        if course == 'شعبہ کتب':
            subjects = [s for s in all_subjects if s.get('course') == course and s.get('class_name') == class_name]
        else:
            subjects = [s for s in all_subjects if s.get('course') == course]

    if request.method == 'POST':
        try:
            for student in students:
                sid = student.get('student_id')
                subjects_data = {}
                obtained_marks = 0
                total_marks = 0
                
                for subject in subjects:
                    field_name = f"marks_{sid}_{subject.get('id')}"
                    marks = request.POST.get(field_name, 0)
                    try:
                        m_val = int(marks)
                        subjects_data[subject.get('name')] = m_val
                        obtained_marks += m_val
                        total_marks += 100 # Default per subject
                    except: pass
                
                if not subjects_data: continue

                # Calculate Result
                percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
                grade = 'راسب (Fail)'
                if percentage >= 90: grade = 'ممتاز (A+)'
                elif percentage >= 80: grade = 'بہت اچھا (A)'
                elif percentage >= 70: grade = 'اچھا (B)'
                elif percentage >= 60: grade = 'مقبول (C)'
                elif percentage >= 50: grade = 'کوشش درکار (D)'

                res_id = f"{sid}_{year}_{exam_type}"
                result_data = {
                    'student_id': sid,
                    'year': year,
                    'exam_type': exam_type,
                    'subjects_json': subjects_data,
                    'obtained_marks': obtained_marks,
                    'total_marks': total_marks,
                    'percentage': round(percentage, 1),
                    'overall_grade': grade
                }
                firebase_utils.save_document('results', res_id, result_data)
            
            messages.success(request, "Results saved successfully.")
            return redirect(f"{request.path}?course={course}&class_name={class_name}&year={year}&exam_type={exam_type}")
        except Exception as e:
            messages.error(request, f"Error saving results: {e}")

    current_results = {}
    if students:
        all_res = firebase_utils.list_documents('results')
        for r in all_res:
            if r.get('year') == year and r.get('exam_type') == exam_type:
                current_results[r.get('student_id')] = r.get('subjects_json')

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
    student = firebase_utils.get_document('students', student_id)
    res_id = f"{student_id}_{year}_{exam_type}"
    result = firebase_utils.get_document('results', res_id)
    if not student or not result:
        messages.error(request, "Result not found.")
        return redirect('academy:directory')
    return render(request, 'academy/result_card.html', {
        'student': student,
        'result': result,
        'subjects': result.get('subjects_json', {})
    })

def class_gazette(request):
    course = request.GET.get('course')
    class_name = request.GET.get('class_name')
    year = request.GET.get('year', '2024')
    exam_type = request.GET.get('exam_type', 'سالانہ امتحان')

    results = []
    subjects_list = []
    
    if course and class_name:
        all_res = firebase_utils.list_documents('results')
        all_students = firebase_utils.list_documents('students')
        student_map = {s['student_id']: s for s in all_students}
        
        # Filter results for this class
        class_results = []
        for r in all_res:
            sid = r.get('student_id')
            student = student_map.get(sid)
            if student and student.get('course') == course and \
               student.get('desired_class') == class_name and \
               r.get('year') == year and r.get('exam_type') == exam_type:
                r['student'] = student
                class_results.append(r)
        
        # Determine all subjects
        all_subs = set()
        for r in class_results:
            for sub in r.get('subjects_json', {}).keys():
                all_subs.add(sub)
        subjects_list = sorted(list(all_subs))
        
        # Ranking
        class_results = sorted(class_results, key=lambda x: x.get('obtained_marks', 0), reverse=True)
        current_rank = 0
        last_marks = -1
        for i, r in enumerate(class_results):
            if r.get('obtained_marks') != last_marks:
                current_rank = i + 1
            r['position'] = current_rank
            last_marks = r.get('obtained_marks')
            r['marks_list'] = [r.get('subjects_json', {}).get(s, '-') for s in subjects_list]
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
    student = firebase_utils.get_document('students', student_id)
    if not student:
        return redirect('academy:directory')
    
    all_res = firebase_utils.list_documents('results')
    results = [r for r in all_res if r.get('student_id') == student_id]
    results = sorted(results, key=lambda x: (x.get('year'), x.get('exam_type')))
    
    total_obtained = sum(r.get('obtained_marks', 0) for r in results)
    total_possible = sum(r.get('total_marks', 0) for r in results)
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

