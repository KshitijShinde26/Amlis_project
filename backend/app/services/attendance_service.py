import io
import pandas as pd
from sqlalchemy.orm import Session
from app.models.database import Student, Subject, AttendanceRecord, AnomalyResult
from app.ml.preprocessing import validate_and_preprocess_dataframe

def process_and_save_attendance(file_contents: bytes, filename: str, db: Session):
    """
    Parses CSV/Excel file, validates data, auto-populates Student and Subject tables,
    and inserts attendance records into database with intra-batch and cross-DB deduplication.
    Uses a single atomic database transaction.
    """
    # 1. Read file format
    if filename.endswith('.csv'):
        try:
            df = pd.read_csv(io.BytesIO(file_contents))
        except pd.errors.EmptyDataError:
            raise ValueError("Uploaded file is empty. Please provide a valid CSV or Excel file.")
    elif filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(io.BytesIO(file_contents))
        except Exception:
            raise ValueError("Could not read Excel file. Please ensure it is a valid format.")
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel (.xlsx) file.")

    if df.empty:
        raise ValueError("Uploaded file contains no data rows. Please provide attendance records.")

    records_received = len(df)

    # 2. Validate & Preprocess
    df_clean, warnings, dropped_count = validate_and_preprocess_dataframe(df, return_details=True)

    if df_clean.empty:
        raise ValueError("No valid records found in the uploaded file after validation.")

    # 3. Deduplicate within the uploaded batch
    # Unique record identity: (student_id, attendance_date, subject_code, attendance_time)
    initial_clean_count = len(df_clean)
    df_clean = df_clean.drop_duplicates(
        subset=['student_id', 'attendance_date', 'subject_code', 'attendance_time'],
        keep='first'
    )
    intra_batch_duplicates = initial_clean_count - len(df_clean)

    # 4. Check against existing records in the database
    # Query existing identities for the students/dates present in this batch
    batch_students = df_clean['student_id'].astype(str).unique().tolist()
    batch_dates = df_clean['attendance_date'].unique().tolist()

    existing_query = db.query(
        AttendanceRecord.student_id,
        AttendanceRecord.attendance_date,
        AttendanceRecord.subject_code,
        AttendanceRecord.attendance_time
    ).filter(
        AttendanceRecord.student_id.in_(batch_students),
        AttendanceRecord.attendance_date.in_(batch_dates)
    ).all()

    existing_set = {
        (str(r.student_id), r.attendance_date, str(r.subject_code), str(r.attendance_time))
        for r in existing_query
    }

    try:
        # 5. Sync Students into DB (within single transaction)
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

        # 6. Sync Subjects into DB (within single transaction)
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

        # 7. Filter out duplicates and prepare records to insert
        records_to_insert = []
        db_duplicates_count = 0

        for _, row in df_clean.iterrows():
            s_id = str(row['student_id'])
            sub_code = str(row['subject_code'])
            att_date = row['attendance_date']
            att_time = str(row['attendance_time'])
            rec_key = (s_id, att_date, sub_code, att_time)

            if rec_key in existing_set:
                db_duplicates_count += 1
                continue

            sub_obj = subject_map.get(sub_code)
            att_rec = AttendanceRecord(
                student_id=s_id,
                subject_id=sub_obj.id if sub_obj else 1,
                subject_code=sub_code,
                attendance_date=att_date,
                attendance_time=att_time,
                status=row['status']
            )
            records_to_insert.append(att_rec)
            # Add to existing_set to avoid duplicates in the same run if any
            existing_set.add(rec_key)

        if records_to_insert:
            db.bulk_save_objects(records_to_insert)

        # Single atomic commit for students, subjects, and attendance records
        db.commit()

    except Exception:
        db.rollback()
        raise

    total_duplicates = intra_batch_duplicates + db_duplicates_count

    return {
        "status": "success",
        "message": f"Processed {records_received} records: {len(records_to_insert)} inserted, {total_duplicates} duplicates skipped, {dropped_count} invalid skipped.",
        "records_processed": len(records_to_insert),
        "records_received": records_received,
        "records_inserted": len(records_to_insert),
        "duplicates_skipped": total_duplicates,
        "invalid_records_skipped": dropped_count,
        "students_count": len(unique_students),
        "subjects_count": len(unique_subjects),
        "sample_records": df_clean.head(5).to_dict(orient="records"),
        "warnings": warnings
    }
