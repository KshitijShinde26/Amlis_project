import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Time, Text, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100), default="Information Technology")
    semester = Column(Integer, default=6)
    division = Column(String(10), default="A")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
    anomaly_results = relationship("AnomalyResult", back_populates="student", cascade="all, delete-orphan")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_code = Column(String(50), unique=True, index=True, nullable=False)
    subject_name = Column(String(100), nullable=False)
    department = Column(String(100), default="Information Technology")
    semester = Column(Integer, default=6)

    # Relationships
    attendance_records = relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_code = Column(String(50), nullable=False)
    attendance_date = Column(Date, nullable=False, index=True)
    attendance_time = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False) # 'Present' or 'Absent'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")
    anomaly_result = relationship("AnomalyResult", back_populates="attendance_record", uselist=False, cascade="all, delete-orphan")

class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attendance_record_id = Column(Integer, ForeignKey("attendance_records.id", ondelete="CASCADE"), nullable=False, unique=True)
    student_id = Column(String(50), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_score = Column(Float, nullable=False) # e.g. -0.25 (lower = more anomalous in Isolation Forest)
    is_anomaly = Column(Boolean, nullable=False, default=False)
    anomaly_status = Column(String(50), nullable=False) # 'Normal', 'Suspicious', 'Highly Suspicious'
    detection_method = Column(String(50), nullable=False, default="Isolation Forest")
    reason_indicators = Column(Text, nullable=True) # JSON or formatted string of explanation
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    attendance_record = relationship("AttendanceRecord", back_populates="anomaly_result")
    student = relationship("Student", back_populates="anomaly_results")
