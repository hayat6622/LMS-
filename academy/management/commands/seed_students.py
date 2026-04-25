from django.core.management.base import BaseCommand
from django.utils import timezone
from academy.models import Student
import random
from datetime import date, timedelta

URDU_NAMES = [
    'فاطمہ بی بی', 'عائشہ خانم', 'زینب نور', 'مریم طاہر', 'حفصہ احمد',
    'سمیرہ رحیم', 'خدیجہ علی', 'رقیہ یوسف', 'امینہ راشد', 'صفیہ کریم',
    'نور الہدیٰ', 'تسنیم اختر', 'ثناء ملک', 'ہاجرہ شاہ', 'رابعہ ظفر',
    'نجمہ بیگم', 'شمسہ پروین', 'گلناز بی بی', 'نسرین فاطمہ', 'شبنم رانی',
    'محمد علی', 'احمد خان', 'عبداللہ رحیم', 'یوسف ملک', 'حمزہ طاہر',
    'بلال احمد', 'عمر فاروق', 'سلمان قریشی', 'طلحہ اکرم', 'زبیر انصاری',
    'عثمان شاہ', 'ابراہیم ظفر', 'اسماعیل حسین', 'سفیان رضا', 'انس کریم',
    'مصعب علوی', 'حارث بیگ', 'شعیب نوید', 'کاشف محمود', 'نعمان اقبال',
    'عائشہ سلطان', 'حنا ریاض', 'ماریہ جاوید', 'نادیہ وسیم', 'صبا طارق',
    'رشدہ منیر', 'فریحہ کاظم', 'مہوش الیاس', 'زارا امجد', 'لیلیٰ نصیر',
]

URDU_TO_EN = {
    'فاطمہ بی بی': 'Fatima Bibi', 'عائشہ خانم': 'Ayesha Khanum', 'زینب نور': 'Zainab Noor', 
    'مریم طاہر': 'Maryam Tahir', 'حفصہ احمد': 'Hafsa Ahmed', 'سمیرہ رحیم': 'Samira Rahim', 
    'خدیجہ علی': 'Khadija Ali', 'رقیہ یوسف': 'Ruqayya Yusuf', 'امینہ راشد': 'Amina Rashid', 
    'صفیہ کریم': 'Safiya Karim', 'نور الہدیٰ': 'Noor-ul-Huda', 'تسنیم اختر': 'Tasneem Akhtar', 
    'ثناء ملک': 'Sana Malik', 'ہاجرہ شاہ': 'Hajra Shah', 'رابعہ ظفر': 'Rabia Zafar', 
    'نجمہ بیگم': 'Najma Begum', 'شمسہ پروین': 'Shamsa Parveen', 'گلناز بی بی': 'Gulnaz Bibi', 
    'نسرین فاطمہ': 'Nasreen Fatima', 'شبنم رانی': 'Shabnam Rani', 'محمد علی': 'Muhammad Ali', 
    'احمد خان': 'Ahmed Khan', 'عبداللہ رحیم': 'Abdullah Rahim', 'یوسف ملک': 'Yusuf Malik', 
    'حمزہ طاہر': 'Hamza Tahir', 'بلال احمد': 'Bilal Ahmed', 'عمر فاروق': 'Umar Farooq', 
    'سلمان قریشی': 'Salman Qureshi', 'طلحہ اکرم': 'Talha Akram', 'زبیر انصاری': 'Zubair Ansari', 
    'عثمان شاہ': 'Usman Shah', 'ابراہیم ظفر': 'Ibrahim Zafar', 'اسماعیل حسین': 'Ismail Hussain', 
    'سفیان رضا': 'Sufyan Raza', 'انس کریم': 'Anas Karim', 'مصعب علوی': 'Musab Alvi', 
    'حارث بیگ': 'Haris Baig', 'شعیب نوید': 'Shoaib Naveed', 'کاشف محمود': 'Kashif Mehmood', 
    'نعمان اقبال': 'Noman Iqbal', 'عائشہ سلطان': 'Ayesha Sultan', 'حنا ریاض': 'Hina Riaz', 
    'ماریہ جاوید': 'Maria Javed', 'نادیہ وسیم': 'Nadia Waseem', 'صبا طارق': 'Saba Tariq', 
    'رشدہ منیر': 'Rushda Munir', 'فریحہ کاظم': 'Fariha Kazim', 'مہوش الیاس': 'Mehwish Ilyas', 
    'زارا امجد': 'Zara Amjad', 'لیلیٰ نصیر': 'Laila Naseer'
}

GUARDIAN_NAMES = [
    'محمد اقبال', 'عبدالرحمٰن', 'غلام محمد', 'رحیم بخش', 'نور محمد',
    'محمد یوسف', 'محمد حنیف', 'عبدالکریم', 'محمد رمضان', 'عبداللہ خان',
]

GUARDIAN_RELATIONS = ['والد', 'والدہ', 'بھائی', 'چچا', 'ماموں', 'دادا', 'نانا']

ADDRESSES = [
    'گلی نمبر ۳، محلہ حسن پورہ، لاہور',
    'مکان نمبر ۱۲، گلیلی روڈ، ملتان',
    'بلاک بی، ٹاؤن شپ، کراچی',
    'قریب جامع مسجد، راولپنڈی',
    'محلہ نور بخش، فیصل آباد',
    'گوکھرو روڈ، گجرات',
    'قریب ریلوے اسٹیشن، پشاور',
    'کنجروڑ روڈ، حیدرآباد',
    'شاہ عالم مارکیٹ، لاہور',
    'سڑک نمبر ۵، کوئٹہ',
]

DESIRED_CLASSES = ['درجہ اولیٰ', 'درجہ ثانیہ', 'درجہ ثالثہ', 'درجہ رابعہ', 'درجہ خامسہ', 'درجہ سادسہ', 'درجہ سابعہ']
FIRST_CLASSES = ['ناظرہ', 'حفظ اول', 'قاعدہ', 'درجہ اول']
DURATIONS = ['۱ سال', '۲ سال', '۳ سال', '۶ ماہ', '۱ سال ۶ ماہ']
LEFT_CLASSES = ['درجہ سوم', 'درجہ چہارم', 'درجہ دوم', '']
RETURNED_CLASSES = ['درجہ اول', 'درجہ دوم', 'درجہ سوم', '']
REASONS = ['گھریلو مجبوری', 'صحت کی خرابی', 'سفر', 'مالی مشکلات', '']

COURSES = [
    'شعبہ حفظ و ناظرہ',
    'شعبہ کتب',
    'شعبہ بنین',
]


class Command(BaseCommand):
    help = 'Seed 50 demo students into the database'

    def handle(self, *args, **kwargs):
        created = 0
        for i, urdu_name in enumerate(URDU_TO_EN.keys()):
            dob = date(2005, 1, 1) + timedelta(days=random.randint(0, 365 * 8))
            has_leaving = random.random() < 0.3  # 30% have leaving info

            course = COURSES[i % 3]
            student = Student(
                name=urdu_name,
                name_en=URDU_TO_EN.get(urdu_name, ''),
                guardian_name=random.choice(GUARDIAN_NAMES),
                guardian_relation=random.choice(GUARDIAN_RELATIONS),
                contact_number=f'03{random.randint(10,49)}{random.randint(1000000,9999999)}',
                address=random.choice(ADDRESSES),
                course=course,
                enrollment_date=date(2024, random.randint(1, 12), random.randint(1, 28)),
                attendance_score=round(random.uniform(60.0, 100.0), 1),
                desired_class=random.choice(DESIRED_CLASSES) if course == 'شعبہ کتب' else '',
                date_of_birth=dob,
                first_class_in_jamia=random.choice(FIRST_CLASSES),
                wifaq_registration_number=f'WM-{random.randint(10000, 99999)}',
                roll_number=f'R-{random.randint(100, 999)}',
                father_cnic=f'{random.randint(10000,49999)}-{random.randint(1000000,9999999)}-{random.randint(1,9)}',
                duration_of_education=random.choice(DURATIONS),
                left_class_year=random.choice(LEFT_CLASSES) if has_leaving else '',
                returned_to_class=random.choice(RETURNED_CLASSES) if has_leaving else '',
                reason_for_leaving=random.choice(REASONS) if has_leaving else '',
                date_of_leaving=date(2024, random.randint(1, 6), random.randint(1, 28)) if has_leaving else None,
            )
            student.save()
            created += 1
            self.stdout.write(f'  [{created:02d}] Created: {student.student_id}')

        self.stdout.write(self.style.SUCCESS(f'Done! Successfully created {created} demo students.'))
