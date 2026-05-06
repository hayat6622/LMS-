import os
import django
import sys
from django.utils import timezone

# Set up Django environment
sys.path.append('D:\\projects 2026\\lms_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from academy.models import Student, Attendance

def sync_sahib_tarteeb():
    last_year = timezone.now().date() - timezone.timedelta(days=365)
    students = Student.objects.all()
    count = 0
    for student in students:
        has_absence = student.attendances.filter(date__gte=last_year, status='Absent').exists()
        total_late = student.total_late_minutes_last_year()
        
        # New criteria: No absences and < 60 mins late
        if not has_absence and total_late < 60:
            student.is_sahib_tarteeb = True
        else:
            student.is_sahib_tarteeb = False
        student.save()
        if student.is_sahib_tarteeb:
            count += 1
    print(f"Sync complete. {count} students are now Sahib Tarteeb.")

if __name__ == '__main__':
    sync_sahib_tarteeb()
