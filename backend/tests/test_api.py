import pytest
import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import get_db
from app.models.database import Base, Student, Subject, AttendanceRecord

# Setup in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

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
