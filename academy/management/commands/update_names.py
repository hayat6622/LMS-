from django.core.management.base import BaseCommand
from academy.models import Student

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

class Command(BaseCommand):
    help = 'Update existing students with English names'

    def handle(self, *args, **kwargs):
        updated = 0
        for student in Student.objects.all():
            if student.name in URDU_TO_EN and (not student.name_en or student.name_en == ""):
                student.name_en = URDU_TO_EN[student.name]
                student.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated} students with English names."))
