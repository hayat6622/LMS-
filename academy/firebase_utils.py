from django.conf import settings
from firebase_admin import firestore

def get_db():
    """Returns the Firestore client."""
    try:
        return firestore.client()
    except Exception:
        return None

def get_collection(collection_name):
    """Returns a collection reference."""
    db = get_db()
    if db:
        return db.collection(collection_name)
    return None

def save_document(collection_name, doc_id, data):
    """Saves or updates a document in a collection."""
    doc_ref = get_collection(collection_name).document(str(doc_id))
    doc_ref.set(data, merge=True)
    return doc_ref

def get_document(collection_name, doc_id):
    """Retrieves a document from a collection."""
    doc_ref = get_collection(collection_name).document(str(doc_id))
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def delete_document(collection_name, doc_id):
    """Deletes a document from a collection."""
    get_collection(collection_name).document(str(doc_id)).delete()

def list_documents(collection_name):
    """Lists all documents in a collection."""
    col_ref = get_collection(collection_name)
    if not col_ref:
        return []
    docs = col_ref.stream()
    return [{**doc.to_dict(), 'id': doc.id} for doc in docs]

# Example mapping for Student model
def sync_student_to_firebase(student):
    """Helper to sync a Django Student instance to Firestore."""
    data = {
        'student_id': student.student_id,
        'name': student.name,
        'name_en': student.name_en,
        'guardian_name': student.guardian_name,
        'guardian_relation': student.guardian_relation,
        'contact_number': student.contact_number,
        'address': student.address,
        'course': student.course,
        'enrollment_date': str(student.enrollment_date) if student.enrollment_date else '',
        'attendance_score': student.attendance_score,
        'desired_class': student.desired_class,
        'date_of_birth': str(student.date_of_birth) if student.date_of_birth else '',
        'first_class_in_jamia': student.first_class_in_jamia,
        'wifaq_registration_number': student.wifaq_registration_number,
        'roll_number': student.roll_number,
        'father_cnic': student.father_cnic,
        'left_class_year': student.left_class_year,
        'returned_to_class': student.returned_to_class,
        'reason_for_leaving': student.reason_for_leaving,
        'date_of_leaving': str(student.date_of_leaving) if student.date_of_leaving else '',
        'duration_of_education': student.duration_of_education,
        'monthly_fee': student.monthly_fee,
        'personal_contribution': student.personal_contribution,
        'is_sahib_tarteeb': student.is_sahib_tarteeb,
    }
    save_document('students', student.student_id, data)

def sync_attendance_to_firebase(attendance):
    """Helper to sync a Django Attendance instance to Firestore."""
    data = {
        'student_id': attendance.student.student_id,
        'date': str(attendance.date),
        'status': attendance.status,
        'minutes_late': attendance.minutes_late,
        'sms_sent': attendance.sms_sent
    }
    att_id = f"{attendance.student.student_id}_{attendance.date}"
    save_document('attendance', att_id, data)

def sync_result_to_firebase(result):
    """Helper to sync a Django Result instance to Firestore."""
    data = {
        'student_id': result.student.student_id,
        'year': result.year,
        'exam_type': result.exam_type,
        'subjects_json': result.subjects_json,
        'obtained_marks': result.obtained_marks,
        'total_marks': result.total_marks,
        'percentage': result.percentage,
        'overall_grade': result.overall_grade,
        'remarks': result.remarks
    }
    res_id = f"{result.student.student_id}_{result.year}_{result.exam_type}"
    save_document('results', res_id, data)

def sync_staff_to_firebase(staff):
    """Helper to sync a Django Staff instance to Firestore."""
    data = {
        'staff_id': staff.staff_id,
        'name': staff.name,
        'role': staff.role,
        'contact_number': staff.contact_number,
        'salary': staff.salary,
        'assigned_class': staff.assigned_class,
        'duration': staff.duration,
        'address': staff.address
    }
    save_document('staff', staff.staff_id, data)
