import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class StudentBase(BaseModel):
    student_id: str
    name: str
    department: Optional[str] = "Information Technology"
    semester: Optional[int] = 6
    division: Optional[str] = "A"

class StudentResponse(StudentBase):
    id: int
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class SubjectBase(BaseModel):
    subject_code: str
    subject_name: str
    department: Optional[str] = "Information Technology"
    semester: Optional[int] = 6

class SubjectResponse(SubjectBase):
    id: int

    class Config:
        from_attributes = True

class AttendanceRecordBase(BaseModel):
    student_id: str
    subject_code: str
    attendance_date: datetime.date
    attendance_time: str
    status: str

class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    subject_id: int
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class AnomalyResultResponse(BaseModel):
    id: int
    attendance_record_id: int
    student_id: str
    student_name: Optional[str] = None
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    attendance_date: Optional[datetime.date] = None
    attendance_time: Optional[str] = None
    attendance_status: Optional[str] = None
    anomaly_score: float
    is_anomaly: bool
    anomaly_status: str
    detection_method: str
    reason_indicators: Optional[str] = None
    detected_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    status: str
    message: str
    records_processed: int
    students_count: int
    subjects_count: int
    sample_records: List[Dict[str, Any]] = []

class DetectionRequest(BaseModel):
    contamination: Optional[float] = 0.10
    method: Optional[str] = "Isolation Forest"

class DetectionResponse(BaseModel):
    status: str
    message: str
    total_analyzed: int
    anomalies_detected: int
    anomaly_percentage: float
    summary_metrics: Dict[str, Any]

class DashboardStats(BaseModel):
    total_students: int
    total_subjects: int
    total_records: int
    present_records: int
    absent_records: int
    normal_records: int
    anomalous_records: int
    anomaly_percentage: float
    top_suspicious_students: List[Dict[str, Any]]
    subject_wise_stats: List[Dict[str, Any]]
    attendance_trends: List[Dict[str, Any]]
