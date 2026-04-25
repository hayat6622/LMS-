from django import forms
from .models import Student, Staff, Subject
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'name_en', 'date_of_birth', 'guardian_name', 'guardian_relation',
            'contact_number', 'address', 'course', 'desired_class',
            'first_class_in_jamia', 'wifaq_registration_number', 'roll_number',
            'father_cnic', 'left_class_year', 'returned_to_class',
            'reason_for_leaving', 'date_of_leaving', 'duration_of_education',
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
            'first_class_in_jamia': 'جامعہ میں پہلا درجہ / First Class in Jamia',
            'wifaq_registration_number': 'وفاق المدارس رقم التسجیل / Wifaq Reg. No.',
            'roll_number': 'رقم الجلوس / Roll Number',
            'father_cnic': 'والد کا شناختی کارڈ نمبر / Father CNIC',
            'left_class_year': 'کونسے درجے/سال میں چلی گئی / Left Class/Year',
            'returned_to_class': 'واپس کونسے درجہ میں آئی / Returned to Class',
            'reason_for_leaving': 'وجہ اخراج / Reason for Leaving',
            'date_of_leaving': 'تاریخ اخراج / Date of Leaving',
            'duration_of_education': 'مدت تعلیم / Duration of Education',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'reason_for_leaving': forms.Textarea(attrs={'rows': 2}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_of_leaving': forms.DateInput(attrs={'type': 'date'}),
            'desired_class': forms.Select(choices=[('', '---------')] + Student.KUTUB_CLASS_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                    Column('course', css_class='form-group col-md-6 mb-0 w-full'),
                    Column('desired_class', css_class='form-group col-md-6 mb-0 w-full'),
                    css_class='grid grid-cols-1 md:grid-cols-2 gap-4'
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

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_id', 'name', 'role', 'contact_number', 'salary', 'assigned_class', 'duration', 'address']
        labels = {
            'staff_id': 'Staff ID / عملہ آئی ڈی',
            'name': 'نام / Name',
            'role': 'عہدہ / Role',
            'contact_number': 'رابطہ نمبر / Contact Number',
            'salary': 'تنخواہ / Salary',
            'assigned_class': 'کلاس / Assigned Class',
            'duration': 'مدت / Duration',
            'address': 'پتہ / Address',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

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
class SubjectForm(forms.ModelForm):
    COURSE_OPTS = [
        ('شعبہ حفظ و ناظرہ', 'شعبہ حفظ و ناظرہ'),
        ('شعبہ کتب', 'شعبہ کتب'),
        ('شعبہ بنین', 'شعبہ بنین'),
    ]
    CLASS_OPTS = [
        ('', '---'),
        ('درجہ اولیٰ', 'درجہ اولیٰ'),
        ('درجہ ثانیہ', 'درجہ ثانیہ'),
        ('درجہ ثالثہ', 'درجہ ثالثہ'),
        ('درجہ رابعہ', 'درجہ رابعہ'),
        ('درجہ خامسہ', 'درجہ خامسہ'),
        ('درجہ سادسہ', 'درجہ سادسہ'),
        ('درجہ سابعہ', 'درجہ سابعہ'),
    ]

    name = forms.CharField(label='مضمون کا نام', widget=forms.TextInput(attrs={'data-ur': 'مضمون کا نام', 'data-en': 'Subject Name'}))
    course = forms.ChoiceField(label='شعبہ', choices=COURSE_OPTS)
    class_name = forms.ChoiceField(label='درجہ', choices=CLASS_OPTS, required=False)
    total_marks = forms.IntegerField(label='کل نمبر', widget=forms.NumberInput(attrs={'data-ur': 'کل نمبر', 'data-en': 'Total Marks'}))

    class Meta:
        model = Subject
        fields = ['name', 'course', 'class_name', 'total_marks']
