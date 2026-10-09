from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.database import Subject, AttendanceRecord, AnomalyResult

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.get("")
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    res = []
    for sub in subjects:
        total = db.query(AttendanceRecord).filter(AttendanceRecord.subject_id == sub.id).count()
        present = db.query(AttendanceRecord).filter(
            AttendanceRecord.subject_id == sub.id,
            AttendanceRecord.status == "Present"
        ).count()
        absent = total - present
        anomalies = db.query(AnomalyResult).join(
            AttendanceRecord, AnomalyResult.attendance_record_id == AttendanceRecord.id
        ).filter(AttendanceRecord.subject_id == sub.id, AnomalyResult.is_anomaly == True).count()

        res.append({
            "id": sub.id,
            "subject_code": sub.subject_code,
            "subject_name": sub.subject_name,
            "department": sub.department,
            "semester": sub.semester,
            "total_records": total,
            "present_records": present,
            "absent_records": absent,
            "attendance_percentage": round((present / total * 100.0) if total > 0 else 0.0, 1),
            "anomalies_count": anomalies
        })

    return res
