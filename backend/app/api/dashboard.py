from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database.session import get_db
from app.models.database import Student, Subject, AttendanceRecord, AnomalyResult

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/statistics")
def get_dashboard_statistics(db: Session = Depends(get_db)):
    total_students = db.query(Student).count()
    total_subjects = db.query(Subject).count()
    total_records = db.query(AttendanceRecord).count()

    present_count = db.query(AttendanceRecord).filter(AttendanceRecord.status == "Present").count()
    absent_count = total_records - present_count

    anomalous_records = db.query(AnomalyResult).filter(AnomalyResult.is_anomaly == True).count()
    normal_records = db.query(AnomalyResult).filter(AnomalyResult.is_anomaly == False).count()

    anomaly_pct = round((anomalous_records / total_records * 100.0) if total_records > 0 else 0.0, 2)

    # Top Suspicious Students
    top_students_query = db.query(
        AnomalyResult.student_id,
        Student.name.label("student_name"),
        func.count(AnomalyResult.id).label("anomaly_count"),
        func.avg(AnomalyResult.anomaly_score).label("avg_anomaly_score")
    ).join(Student, AnomalyResult.student_id == Student.student_id)\
     .filter(AnomalyResult.is_anomaly == True)\
     .group_by(AnomalyResult.student_id, Student.name)\
     .order_by(func.count(AnomalyResult.id).desc())\
     .limit(5).all()

    top_suspicious = []
    for t in top_students_query:
        top_suspicious.append({
            "student_id": t.student_id,
            "student_name": t.student_name,
            "anomaly_count": t.anomaly_count,
            "avg_anomaly_score": round(float(t.avg_anomaly_score), 2)
        })

    # Subject-wise attendance distribution
    subject_stats = []
    subjects = db.query(Subject).all()
    for sub in subjects:
        sub_total = db.query(AttendanceRecord).filter(AttendanceRecord.subject_id == sub.id).count()
        sub_present = db.query(AttendanceRecord).filter(
            AttendanceRecord.subject_id == sub.id,
            AttendanceRecord.status == "Present"
        ).count()
        sub_anomalies = db.query(AnomalyResult).join(
            AttendanceRecord, AnomalyResult.attendance_record_id == AttendanceRecord.id
        ).filter(AttendanceRecord.subject_id == sub.id, AnomalyResult.is_anomaly == True).count()

        subject_stats.append({
            "subject_code": sub.subject_code,
            "subject_name": sub.subject_name,
            "total_records": sub_total,
            "present_records": sub_present,
            "attendance_rate": round((sub_present / sub_total * 100.0) if sub_total > 0 else 0.0, 1),
            "anomalies_count": sub_anomalies
        })

    # Attendance trend by Date
    all_recs = db.query(AttendanceRecord.attendance_date, AttendanceRecord.status).all()
    trend_dict = {}
    for date_val, status_val in all_recs:
        d_str = str(date_val)
        if d_str not in trend_dict:
            trend_dict[d_str] = {"total": 0, "present": 0}
        trend_dict[d_str]["total"] += 1
        if status_val == "Present":
            trend_dict[d_str]["present"] += 1

    attendance_trends = []
    for d_str in sorted(trend_dict.keys())[:15]:
        tot = trend_dict[d_str]["total"]
        pres = trend_dict[d_str]["present"]
        attendance_trends.append({
            "date": d_str,
            "total": tot,
            "present": pres,
            "absent": tot - pres,
            "attendance_rate": round((pres / tot * 100.0) if tot > 0 else 0.0, 1)
        })

    return {
        "total_students": total_students,
        "total_subjects": total_subjects,
        "total_records": total_records,
        "present_records": present_count,
        "absent_records": absent_count,
        "normal_records": normal_records,
        "anomalous_records": anomalous_records,
        "anomaly_percentage": anomaly_pct,
        "top_suspicious_students": top_suspicious,
        "subject_wise_stats": subject_stats,
        "attendance_trends": attendance_trends
    }
