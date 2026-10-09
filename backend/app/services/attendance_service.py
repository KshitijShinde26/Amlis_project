import io
import pandas as pd
from sqlalchemy.orm import Session
from app.models.database import Student, Subject, AttendanceRecord, AnomalyResult
from app.ml.preprocessing import validate_and_preprocess_dataframe

def process_and_save_attendance(file_contents: bytes, filename: str, db: Session):
    """
    Parses CSV/Excel file, validates data, auto-populates Student and Subject tables,
    and inserts attendance records into database.
    """
    # Read file format
    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_contents))
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(file_contents))
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel (.xlsx) file.")

    # Validate & Preprocess
    df_clean = validate_and_preprocess_dataframe(df)

    # 1. Sync Students into DB
    unique_students = df_clean[['student_id', 'student_name']].drop_duplicates()
    student_map = {}
    for _, row in unique_students.iterrows():
        s_id = str(row['student_id'])
        s_name = str(row['student_name'])
        existing = db.query(Student).filter(Student.student_id == s_id).first()
        if not existing:
            new_student = Student(student_id=s_id, name=s_name)
            db.add(new_student)
            db.flush()
            student_map[s_id] = new_student
        else:
            if existing.name != s_name and s_name != s_id:
                existing.name = s_name
            student_map[s_id] = existing

    # 2. Sync Subjects into DB
    unique_subjects = df_clean[['subject_code', 'subject_name']].drop_duplicates()
    subject_map = {}
    for _, row in unique_subjects.iterrows():
        sub_code = str(row['subject_code'])
        sub_name = str(row['subject_name'])
        existing = db.query(Subject).filter(Subject.subject_code == sub_code).first()
        if not existing:
            new_subject = Subject(subject_code=sub_code, subject_name=sub_name)
            db.add(new_subject)
            db.flush()
            subject_map[sub_code] = new_subject
        else:
            subject_map[sub_code] = existing

    db.commit()

    # 3. Save Attendance Records
    records_to_insert = []
    for _, row in df_clean.iterrows():
        s_id = str(row['student_id'])
        sub_code = str(row['subject_code'])
        sub_obj = subject_map.get(sub_code)
        
        att_rec = AttendanceRecord(
            student_id=s_id,
            subject_id=sub_obj.id if sub_obj else 1,
            subject_code=sub_code,
            attendance_date=row['attendance_date'],
            attendance_time=str(row['attendance_time']),
            status=row['status']
        )
        records_to_insert.append(att_rec)

    db.bulk_save_objects(records_to_insert)
    db.commit()

    return {
        "status": "success",
        "message": f"Successfully parsed and stored {len(records_to_insert)} attendance records.",
        "records_processed": len(records_to_insert),
        "students_count": len(unique_students),
        "subjects_count": len(unique_subjects),
        "sample_records": df_clean.head(5).to_dict(orient="records")
    }
