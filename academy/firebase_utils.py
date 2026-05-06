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
        'contact_number': student.contact_number,
        'course': student.course,
        'enrollment_date': str(student.enrollment_date),
        'is_sahib_tarteeb': student.is_sahib_tarteeb,
        # Add other fields as needed
    }
    save_document('students', student.student_id, data)
