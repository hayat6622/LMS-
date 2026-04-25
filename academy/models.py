from django.db import models
from django.utils import timezone

class Student(models.Model):
    COURSE_CHOICES = [
        ('شعبہ حفظ و ناظرہ', 'شعبہ حفظ و ناظرہ'),
        ('شعبہ کتب', 'شعبہ کتب'),
        ('شعبہ بنین', 'شعبہ بنین'),
    ]
    
    KUTUB_CLASS_CHOICES = [
        ('درجہ اولیٰ', 'درجہ اولیٰ'),
        ('درجہ ثانیہ', 'درجہ ثانیہ'),
        ('درجہ ثالثہ', 'درجہ ثالثہ'),
        ('درجہ رابعہ', 'درجہ رابعہ'),
        ('درجہ خامسہ', 'درجہ خامسہ'),
        ('درجہ سادسہ', 'درجہ سادسہ'),
        ('درجہ سابعہ', 'درجہ سابعہ'),
    ]


    student_id = models.CharField(max_length=20, primary_key=True, unique=True, blank=True)
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, verbose_name='انگریزی نام / English Name')
    guardian_name = models.CharField(max_length=100)
    guardian_relation = models.CharField(max_length=100, blank=True, verbose_name='سرپرست کا طالبہ سے رشتہ')
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    enrollment_date = models.DateField(default=timezone.now)
    attendance_score = models.FloatField(default=100.0)

    # Additional Academic Fields
    desired_class = models.CharField(max_length=100, blank=True, verbose_name='مطلوبہ درجہ')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='تاریخ پیدائش')
    first_class_in_jamia = models.CharField(max_length=100, blank=True, verbose_name='جامعہ میں پہلا درجہ')
    wifaq_registration_number = models.CharField(max_length=50, blank=True, verbose_name='وفاق المدارس رقم التسجیل')
    roll_number = models.CharField(max_length=50, blank=True, verbose_name='رقم الجلوس')
    father_cnic = models.CharField(max_length=20, blank=True, verbose_name='والد کا شناختی کارڈ نمبر')
    left_class_year = models.CharField(max_length=100, blank=True, verbose_name='کونسے درجے/سال میں چلی گئی')
    returned_to_class = models.CharField(max_length=100, blank=True, verbose_name='واپس کونسے درجہ میں آئی')
    reason_for_leaving = models.TextField(blank=True, verbose_name='وجہ اخراج')
    date_of_leaving = models.DateField(null=True, blank=True, verbose_name='تاریخ اخراج')
    duration_of_education = models.CharField(max_length=100, blank=True, verbose_name='مدت تعلیم')

    def save(self, *args, **kwargs):
        if not self.student_id:
            current_year = timezone.now().year
            last_student = Student.objects.filter(student_id__startswith=f'IA-{current_year}-').order_by('-student_id').first()
            if last_student:
                last_id_num = int(last_student.student_id.split('-')[-1])
                new_id_num = last_id_num + 1
            else:
                new_id_num = 1
            self.student_id = f'IA-{current_year}-{new_id_num:04d}'
        
        # Enforce that only 'شعبہ کتب' has a desired class
        if self.course != 'شعبہ کتب':
            self.desired_class = ''
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class Staff(models.Model):
    ROLE_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Editor', 'Editor'),
        ('Teacher', 'Teacher'),
    ]

    staff_id = models.CharField(max_length=20, primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    contact_number = models.CharField(max_length=20)
    salary = models.CharField(max_length=50, blank=True, verbose_name='تنخواہ')
    assigned_class = models.CharField(max_length=100, blank=True, verbose_name='کلاس')
    duration = models.CharField(max_length=100, blank=True, verbose_name='مدت')
    address = models.TextField(blank=True, verbose_name='پتہ')

    def __str__(self):
        return f"{self.staff_id} - {self.name} ({self.role})"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    sms_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.status})"

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.student.name} - {self.start_date} to {self.end_date} ({self.status})"

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='مضمون کا نام')
    course = models.CharField(max_length=50, choices=Student.COURSE_CHOICES, verbose_name='شعبہ')
    class_name = models.CharField(max_length=100, blank=True, verbose_name='درجہ')
    total_marks = models.IntegerField(default=100, verbose_name='کل نمبر')

    def __str__(self):
        return f"{self.name} ({self.course} - {self.class_name})"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    year = models.CharField(max_length=4, verbose_name='سال')
    subjects_json = models.JSONField(default=dict, help_text="Store dict of subjects e.g. {'نحو': 90, 'صرف': 85}")
    total_marks = models.IntegerField(default=0, verbose_name='کل نمبر')
    obtained_marks = models.IntegerField(default=0, verbose_name='حاصل کردہ نمبر')
    percentage = models.FloatField(null=True, blank=True, verbose_name='فیصد')
    overall_grade = models.CharField(max_length=20, blank=True, verbose_name='گریڈ')
    remarks = models.TextField(blank=True, verbose_name='کیفیت')

    class Meta:
        unique_together = ('student', 'year')

    def save(self, *args, **kwargs):
        # Calculate total and obtained from subjects_json
        if self.subjects_json:
            self.obtained_marks = sum(int(v) for v in self.subjects_json.values() if str(v).isdigit())
            # For simplicity, we assume each subject is out of 100 or fetched from Subject model
            # But in the result instance, we should probably store what the total expected was.
            # If total_marks is not set, we can estimate it (e.g. 100 * len(subjects))
            if self.total_marks == 0:
                self.total_marks = len(self.subjects_json) * 100
            
            if self.total_marks > 0:
                self.percentage = (self.obtained_marks / self.total_marks) * 100
                
                # Simple Grading Logic
                if self.percentage >= 90: self.overall_grade = 'ممتاز (A+)'
                elif self.percentage >= 80: self.overall_grade = 'بہت اچھا (A)'
                elif self.percentage >= 70: self.overall_grade = 'اچھا (B)'
                elif self.percentage >= 60: self.overall_grade = 'مقبول (C)'
                elif self.percentage >= 50: self.overall_grade = 'کوشش درکار (D)'
                else: self.overall_grade = 'راسب (Fail)'
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.year} ({self.overall_grade})"
