import pytest
import datetime
from pathlib import Path
from tests.conftest import TestingSessionLocal, client
from app.models.database import Student, Subject, AttendanceRecord

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_anomalies_empty():
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test_trigger_anomaly_detection_empty():
    response = client.post("/api/anomaly/detect", json={"contamination": 0.1})
    assert response.status_code == 200
    assert "No attendance records found" in response.json()["message"]

def test_trigger_anomaly_with_data():
    # Insert some fake data
    db = TestingSessionLocal()
    student = Student(student_id="S1", name="Test Student")
    subject = Subject(subject_code="CS101", subject_name="CS")
    db.add(student)
    db.add(subject)
    db.commit()
    
    # 20 identical attendance records
    for i in range(20):
        record = AttendanceRecord(
            student_id="S1",
            subject_id=subject.id,
            subject_code="CS101",
            attendance_date=datetime.date(2023, 10, i+1),
            attendance_time="10:00:00",
            status="Present"
        )
        db.add(record)
    db.commit()
    
    response = client.post("/api/anomaly/detect", json={"contamination": 0.1})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Check if anomalies were retrieved
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    assert response.json()["total"] == 20

def test_download_sample_dataset_success():
    response = client.get("/api/dataset/sample")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'filename="sample_attendance.csv"' in response.headers.get("content-disposition", "")
    assert len(response.text) > 0
    assert "student_id" in response.text.lower()

def test_download_sample_dataset_missing_file(monkeypatch):
    monkeypatch.setattr(Path, "exists", lambda self: False)
    response = client.get("/api/dataset/sample")
    assert response.status_code == 200
    assert response.json() == {"error": "Sample dataset file not found."}

