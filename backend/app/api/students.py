from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.database import Student, AttendanceRecord, AnomalyResult, Subject

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("")
def list_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    res = []
    for s in students:
        total_recs = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == s.student_id).count()
        present_recs = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == s.student_id,
            AttendanceRecord.status == "Present"
        ).count()
        anomalies_cnt = db.query(AnomalyResult).filter(
            AnomalyResult.student_id == s.student_id,
            AnomalyResult.is_anomaly == True
        ).count()
        
        att_pct = round((present_recs / total_recs * 100.0) if total_recs > 0 else 0.0, 1)

        res.append({
            "id": s.id,
            "student_id": s.student_id,
            "name": s.name,
            "department": s.department,
            "semester": s.semester,
            "division": s.division,
            "total_records": total_recs,
            "present_records": present_recs,
            "attendance_percentage": att_pct,
            "anomalies_count": anomalies_cnt,
            "risk_status": "High Risk" if anomalies_cnt >= 3 else ("Medium Risk" if anomalies_cnt >= 1 else "Normal")
        })

    return res

@router.get("/{student_id}")
def get_student_details(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    total_recs = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student_id).count()
    present_recs = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.status == "Present"
    ).count()

    anomalies = db.query(AnomalyResult).filter(
        AnomalyResult.student_id == student_id,
        AnomalyResult.is_anomaly == True
    ).all()

    att_pct = round((present_recs / total_recs * 100.0) if total_recs > 0 else 0.0, 1)

    # Subject-wise attendance for student
    subjects = db.query(Subject).all()
    sub_breakdown = []
    for sub in subjects:
        sub_total = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.subject_id == sub.id
        ).count()
        sub_present = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.subject_id == sub.id,
            AttendanceRecord.status == "Present"
        ).count()
        if sub_total > 0:
            sub_breakdown.append({
                "subject_code": sub.subject_code,
                "subject_name": sub.subject_name,
                "total": sub_total,
                "present": sub_present,
                "percentage": round(sub_present / sub_total * 100.0, 1)
            })

    return {
        "student_id": student.student_id,
        "name": student.name,
        "department": student.department,
        "semester": student.semester,
        "division": student.division,
        "total_records": total_recs,
        "present_records": present_recs,
        "attendance_percentage": att_pct,
        "anomalies_count": len(anomalies),
        "subject_breakdown": sub_breakdown
    }

@router.get("/{student_id}/attendance")
def get_student_attendance_history(student_id: str, db: Session = Depends(get_db)):
    records = db.query(
        AttendanceRecord.id,
        AttendanceRecord.subject_code,
        Subject.subject_name,
        AttendanceRecord.attendance_date,
        AttendanceRecord.attendance_time,
        AttendanceRecord.status,
        AnomalyResult.anomaly_score,
        AnomalyResult.anomaly_status,
        AnomalyResult.reason_indicators
    ).outerjoin(AnomalyResult, AttendanceRecord.id == AnomalyResult.attendance_record_id)\
     .join(Subject, AttendanceRecord.subject_id == Subject.id)\
     .filter(AttendanceRecord.student_id == student_id)\
     .order_by(AttendanceRecord.attendance_date.desc()).all()

    formatted = []
    for r in records:
        formatted.append({
            "id": r.id,
            "subject_code": r.subject_code,
            "subject_name": r.subject_name,
            "date": str(r.attendance_date),
            "time": str(r.attendance_time),
            "status": r.status,
            "anomaly_score": r.anomaly_score if r.anomaly_score is not None else 0.0,
            "anomaly_status": r.anomaly_status or "Not Evaluated",
            "reasons": r.reason_indicators
        })

    return formatted
