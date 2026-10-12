import json
import pandas as pd
from sqlalchemy.orm import Session
from app.models.database import Student, Subject, AttendanceRecord, AnomalyResult
from app.ml.pipeline import run_anomaly_pipeline

def run_database_anomaly_detection(db: Session, contamination: float = 0.10):
    """
    Loads all attendance records from DB, runs ML anomaly pipeline (Isolation Forest + LOF),
    and updates AnomalyResult table in database.
    """
    records = db.query(
        AttendanceRecord.id.label("record_id"),
        AttendanceRecord.student_id,
        AttendanceRecord.subject_code,
        AttendanceRecord.attendance_date,
        AttendanceRecord.attendance_time,
        AttendanceRecord.status,
        Student.name.label("student_name"),
        Subject.subject_name
    ).join(Student, AttendanceRecord.student_id == Student.student_id)\
     .join(Subject, AttendanceRecord.subject_id == Subject.id)\
     .all()

    if not records:
        return {
            "status": "warning",
            "message": "No attendance records found in database. Please upload data first.",
            "total_analyzed": 0,
            "anomalies_detected": 0,
            "anomaly_percentage": 0.0,
            "summary_metrics": {}
        }

    raw_data = []
    for r in records:
        raw_data.append({
            "record_id": r.record_id,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "subject_code": r.subject_code,
            "subject_name": r.subject_name,
            "date": str(r.attendance_date),
            "time": str(r.attendance_time),
            "status": r.status
        })

    raw_df = pd.DataFrame(raw_data)
    
    # Run ML Pipeline
    df_results, summary_metrics = run_anomaly_pipeline(raw_df, contamination=contamination)

    anomaly_objects = []
    for _, row in df_results.iterrows():
        anom_res = AnomalyResult(
            attendance_record_id=int(row['record_id']),
            student_id=str(row['student_id']),
            anomaly_score=float(row['if_anomaly_score']),
            is_anomaly=bool(row['is_anomaly']),
            anomaly_status=str(row['if_status']),
            detection_method="Isolation Forest",
            reason_indicators=row['reason_indicators']
        )
        anomaly_objects.append(anom_res)

    try:
        # Atomic replacement: wipe prior anomaly results and save new ones in one single transaction
        db.query(AnomalyResult).delete()
        if anomaly_objects:
            db.bulk_save_objects(anomaly_objects)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "status": "success",
        "message": "ML Anomaly Detection pipeline executed successfully.",
        "total_analyzed": len(df_results),
        "anomalies_detected": summary_metrics['isolation_forest']['anomalies_detected'],
        "anomaly_percentage": summary_metrics['isolation_forest']['anomaly_percentage'],
        "summary_metrics": summary_metrics
    }

def get_anomaly_results_list(
    db: Session,
    student_id: str = None,
    subject_code: str = None,
    status_filter: str = None,
    anomaly_only: bool = False
):
    """
    Fetches detailed anomaly results joined with Student and Subject metadata.
    """
    query = db.query(
        AnomalyResult.id,
        AnomalyResult.attendance_record_id,
        AnomalyResult.student_id,
        Student.name.label("student_name"),
        AttendanceRecord.subject_code,
        Subject.subject_name,
        AttendanceRecord.attendance_date,
        AttendanceRecord.attendance_time,
        AttendanceRecord.status.label("attendance_status"),
        AnomalyResult.anomaly_score,
        AnomalyResult.is_anomaly,
        AnomalyResult.anomaly_status,
        AnomalyResult.detection_method,
        AnomalyResult.reason_indicators,
        AnomalyResult.detected_at
    ).join(AttendanceRecord, AnomalyResult.attendance_record_id == AttendanceRecord.id)\
     .join(Student, AnomalyResult.student_id == Student.student_id)\
     .join(Subject, AttendanceRecord.subject_id == Subject.id)

    if student_id:
        query = query.filter(AnomalyResult.student_id == student_id)
    if subject_code:
        query = query.filter(AttendanceRecord.subject_code == subject_code)
    if status_filter:
        query = query.filter(AnomalyResult.anomaly_status == status_filter)
    if anomaly_only:
        query = query.filter(AnomalyResult.is_anomaly == True)

    results = query.order_by(AnomalyResult.anomaly_score.desc()).all()

    formatted = []
    for r in results:
        reasons_list = []
        if r.reason_indicators:
            try:
                reasons_list = json.loads(r.reason_indicators)
            except:
                reasons_list = [r.reason_indicators]

        formatted.append({
            "id": r.id,
            "attendance_record_id": r.attendance_record_id,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "subject_code": r.subject_code,
            "subject_name": r.subject_name,
            "attendance_date": str(r.attendance_date),
            "attendance_time": str(r.attendance_time),
            "attendance_status": r.attendance_status,
            "anomaly_score": r.anomaly_score,
            "is_anomaly": r.is_anomaly,
            "anomaly_status": r.anomaly_status,
            "detection_method": r.detection_method,
            "reason_indicators": reasons_list,
            "detected_at": r.detected_at.strftime("%Y-%m-%d %H:%M:%S") if r.detected_at else None
        })

    return formatted
