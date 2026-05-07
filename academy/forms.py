from django import forms
from .models import Student, Staff, Subject
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'name_en', 'date_of_birth', 'guardian_name', 'guardian_relation',
            'contact_number', 'address', 'course', 'desired_class', 'teacher',
            'first_class_in_jamia', 'wifaq_registration_number', 'roll_number',
            'father_cnic', 'left_class_year', 'returned_to_class',
            'reason_for_leaving', 'date_of_leaving', 'duration_of_education',
            'monthly_fee', 'personal_contribution', 'is_sahib_tarteeb',
        ]
        labels = {
            'name': 'مکمل نام / Full Name (Urdu)',
            'name_en': 'انگریزی نام / English Name',
            'date_of_birth': 'تاریخ پیدائش / Date of Birth',
            'guardian_name': 'سرپرست کا نام / Guardian Name',
            'guardian_relation': 'سرپرست کا طالبہ سے رشتہ / Guardian Relation',
            'contact_number': 'رابطہ نمبر / Contact Number',
            'address': 'پتہ / Address',
            'course': 'کورس / Course',
            'desired_class': 'مطلوبہ درجہ / Desired Class',
            'teacher': 'نگراں استاد / Class Teacher',
            'first_class_in_jamia': 'جامعہ میں پہلا درجہ / First Class in Jamia',
            'wifaq_registration_number': 'وفاق المدارس رقم التسجیل / Wifaq Reg. No.',
            'roll_number': 'رقم الجلوس / Roll Number',
            'father_cnic': 'والد کا شناختی کارڈ نمبر / Father CNIC',
            'left_class_year': 'کونسے درجے/سال میں چلی گئی / Left Class/Year',
            'returned_to_class': 'واپس کونسے درجہ میں آئی / Returned to Class',
            'reason_for_leaving': 'وجہ اخراج / Reason for Leaving',
            'date_of_leaving': 'تاریخ اخراج / Date of Leaving',
            'duration_of_education': 'مدت تعلیم / Duration of Education',
            'monthly_fee': 'ماہانہ خرچہ / Monthly Fee',
            'personal_contribution': 'ذاتی تعاون / Personal Contribution',
            'is_sahib_tarteeb': 'صاحب ترتیب / Sahib Tarteeb',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'reason_for_leaving': forms.Textarea(attrs={'rows': 2}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_leaving': forms.DateInput(attrs={'type': 'date'}),
            'desired_class': forms.Select(choices=[('', '---------')] + Student.KUTUB_CLASS_CHOICES + Student.GENERAL_CLASS_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from . import firebase_utils
        
        # Manually populate teacher choices from Firestore
        staff_members = firebase_utils.list_documents('staff')
        teacher_choices = [('', '---------')] + [(s['staff_id'], s['name']) for s in staff_members]
        if 'teacher' in self.fields:
            self.fields['teacher'].queryset = Staff.objects.none()
            self.fields['teacher'].choices = teacher_choices
            self.fields['teacher'].required = False
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            # --- Personal Info ---
            Fieldset(
                'ذاتی معلومات / Personal Information',
                Row(
                    Column('name', css_class='form-group col-md-4 mb-0 w-full'),
                    Column('name_en', css_class='form-group col-md-4 mb-0 w-full'),
                    Column('date_of_birth', css_class='form-group col-md-4 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-3 gap-4'
                ),
                Row(
                    Column('guardian_name', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('guardian_relation', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
                ),
                Row(
                    Column('father_cnic', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('contact_number', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
                ),
                Row(
                    Column('address', css_class='form-group col-md-12 mb-0 w-full'),
                    css_class='mt-4'
                ),
            ),
            # --- Academic Info ---
            Fieldset(
                'تعلیمی معلومات / Academic Information',
                Row(
                    Column('course', css_class='form-group col-md-4 mb-0 w-full'),
                    Column('desired_class', css_class='form-group col-md-4 mb-0 w-full'),
                    Column('teacher', css_class='form-group col-md-4 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-3 gap-4'
                ),
                Row(
                    Column('first_class_in_jamia', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('duration_of_education', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
                ),
                Row(
                    Column('wifaq_registration_number', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('roll_number', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
                ),
                Row(
                    Column('monthly_fee', css_class='form-group col-md-4 mb-0 w-full'),
                    Column('personal_contribution', css_class='form-group col-md-4 mb-0 w-full'),
                    Column('is_sahib_tarteeb', css_class='form-group col-md-4 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-3 gap-4 mt-4'
                ),
            ),
            # --- Leaving Info ---
            Fieldset(
                'اخراج کی تفصیلات / Departure Details (اگر قابل اطلاق ہو)',
                Row(
                    Column('left_class_year', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('returned_to_class', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4'
                ),
                Row(
                    Column('date_of_leaving', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('reason_for_leaving', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
                ),
            ),
        )

class StaffForm(forms.Form):
    staff_id = forms.CharField(max_length=20, label='Staff ID / عملہ آئی ڈی')
    name = forms.CharField(max_length=100, label='نام / Name')
    role = forms.ChoiceField(choices=Staff.ROLE_CHOICES, label='عہدہ / Role')
    contact_number = forms.CharField(max_length=20, label='رابطہ نمبر / Contact Number')
    salary = forms.IntegerField(initial=0, label='تنخواہ / Salary')
    assigned_class = forms.CharField(max_length=100, required=False, label='کلاس / Assigned Class')
    duration = forms.CharField(max_length=100, required=False, label='مدت / Duration')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label='پتہ / Address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('staff_id', css_class='form-group col-md-6 mb-0 w-full'),
                Column('role', css_class='form-group col-md-6 mb-0 w-full'),
                css_class='grid grid-cols-1 md:grid-cols-2 gap-4'
            ),
            Row(
                Column('name', css_class='form-group col-md-6 mb-0 w-full'),
                Column('contact_number', css_class='form-group col-md-6 mb-0 w-full'),
                css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
            ),
            Row(
                Column('salary', css_class='form-group col-md-6 mb-0 w-full'),
                Column('assigned_class', css_class='form-group col-md-6 mb-0 w-full'),
                css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
            ),
            Row(
                Column('duration', css_class='form-group col-md-6 mb-0 w-full'),
                Column('address', css_class='form-group col-md-6 mb-0 w-full'),
                css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'
            ),
        )
class SubjectForm(forms.Form):
    COURSE_OPTS = [
        ('شعبہ حفظ و ناظرہ', 'شعبہ حفظ و ناظرہ'),
        ('شعبہ کتب', 'شعبہ کتب'),
        ('شعبہ بنین', 'شعبہ بنین'),
    ]
    CLASS_OPTS = [('', '---')] + Student.KUTUB_CLASS_CHOICES + Student.GENERAL_CLASS_CHOICES

    name = forms.CharField(label='مضمون کا نام', widget=forms.TextInput(attrs={'data-ur': 'مضمون کا نام', 'data-en': 'Subject Name'}))
    course = forms.ChoiceField(label='شعبہ', choices=COURSE_OPTS)
    class_name = forms.ChoiceField(label='درجہ', choices=CLASS_OPTS, required=False)
    teacher = forms.ChoiceField(label='استاد', required=False)
    total_marks = forms.IntegerField(label='کل نمبر', initial=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from . import firebase_utils
        staff_members = firebase_utils.list_documents('staff')
        self.fields['teacher'].choices = [('', '---------')] + [(s['staff_id'], s['name']) for s in staff_members]

