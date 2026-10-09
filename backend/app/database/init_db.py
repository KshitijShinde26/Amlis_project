from app.database.session import engine, SessionLocal
from app.models.database import Base, Student, Subject, AttendanceRecord, AnomalyResult

def init_db():
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if subjects exist, add standard subjects if not
        existing_subjects = db.query(Subject).count()
        if existing_subjects == 0:
            initial_subjects = [
                Subject(subject_code="IT601", subject_name="Applied Machine Learning", department="Information Technology", semester=6),
                Subject(subject_code="IT602", subject_name="Web Technologies & Frameworks", department="Information Technology", semester=6),
                Subject(subject_code="IT603", subject_name="Database Management Systems", department="Information Technology", semester=6),
                Subject(subject_code="IT604", subject_name="Software Architecture & Engineering", department="Information Technology", semester=6),
                Subject(subject_code="IT605", subject_name="Computer Networks & Security", department="Information Technology", semester=6),
            ]
            db.add_all(initial_subjects)
            db.commit()
            print("Database initialized with default subjects.")
    except Exception as e:
        print(f"Error initializing DB seed data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
