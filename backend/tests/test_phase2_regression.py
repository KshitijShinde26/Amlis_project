import pytest
import io
import datetime
from tests.conftest import TestingSessionLocal, client
from app.models.database import Student, Subject, AttendanceRecord, AnomalyResult

def test_template_download_endpoint():
    response = client.get("/api/dataset/template")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'filename="template_attendance.csv"' in response.headers.get("content-disposition", "")
    lines = [line.strip() for line in response.text.strip().splitlines() if line.strip()]
    assert len(lines) == 11  # 1 header + 10 rows
    assert "student_id" in lines[0].lower()

def test_upload_valid_dataset():
    csv_content = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU101,Alice Smith,2026-03-01,10:00,CS101,Computer Science,Present\n"
        "STU102,Bob Jones,2026-03-01,10:00,CS101,Computer Science,Absent\n"
    )
    files = {"file": ("attendance.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/attendance/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["records_received"] == 2
    assert data["records_inserted"] == 2
    assert data["duplicates_skipped"] == 0
    assert data["invalid_records_skipped"] == 0
    assert data["students_count"] == 2
    assert data["subjects_count"] == 1

def test_deduplication_exact_same_upload():
    csv_content = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU101,Alice Smith,2026-03-01,10:00,CS101,Computer Science,Present\n"
        "STU102,Bob Jones,2026-03-01,10:00,CS101,Computer Science,Absent\n"
    )
    files1 = {"file": ("attendance.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res1 = client.post("/api/attendance/upload", files=files1)
    assert res1.status_code == 200
    assert res1.json()["records_inserted"] == 2

    # Second upload of the exact same content
    files2 = {"file": ("attendance.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res2 = client.post("/api/attendance/upload", files=files2)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["records_received"] == 2
    assert data2["records_inserted"] == 0
    assert data2["duplicates_skipped"] == 2

    # Verify total records in DB is still 2
    att_res = client.get("/api/attendance")
    assert att_res.json()["total"] == 2

def test_deduplication_within_single_csv():
    # CSV containing identical rows in the same upload
    csv_content = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU101,Alice Smith,2026-03-01,10:00,CS101,Computer Science,Present\n"
        "STU101,Alice Smith,2026-03-01,10:00,CS101,Computer Science,Present\n"
        "STU103,Charlie,2026-03-01,10:00,CS101,Computer Science,Present\n"
    )
    files = {"file": ("batch.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post("/api/attendance/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["records_received"] == 3
    assert data["records_inserted"] == 2
    assert data["duplicates_skipped"] == 1

def test_distinct_times_and_subjects_preserved():
    # Same student and date, but different times and subjects should both be inserted
    csv_content = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU101,Alice,2026-03-01,09:00,CS101,Computer Science,Present\n"
        "STU101,Alice,2026-03-01,11:00,CS101,Computer Science,Present\n"
        "STU101,Alice,2026-03-01,09:00,CS102,Data Structures,Present\n"
    )
    files = {"file": ("multi.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post("/api/attendance/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["records_inserted"] == 3
    assert data["duplicates_skipped"] == 0

def test_empty_and_header_only_csv():
    # Completely empty file
    empty_files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    res1 = client.post("/api/attendance/upload", files=empty_files)
    assert res1.status_code == 400
    assert "empty" in res1.json()["detail"].lower()

    # Header-only file
    header_only = "student_id,student_name,date,time,subject_code,subject_name,status\n"
    header_files = {"file": ("header.csv", io.BytesIO(header_only.encode("utf-8")), "text/csv")}
    res2 = client.post("/api/attendance/upload", files=header_files)
    assert res2.status_code == 400
    assert "no data rows" in res2.json()["detail"].lower()

def test_unparseable_date_and_status_warnings():
    csv_content = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU101,Alice,not-a-date,10:00,CS101,CS,Present\n"
        "STU102,Bob,2026-03-01,10:00,CS101,CS,Late\n"
        "STU103,Charlie,2026-03-01,10:00,CS101,CS,CustomUnknownStatus\n"
    )
    files = {"file": ("warnings.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post("/api/attendance/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["records_received"] == 3
    assert data["records_inserted"] == 2
    assert data["invalid_records_skipped"] == 1
    assert len(data["warnings"]) >= 2
    # Late should be accepted, CustomUnknownStatus normalized with warning
    warning_texts = " ".join(data["warnings"])
    assert "Invalid or unparseable date" in warning_texts
    assert "CustomUnknownStatus" in warning_texts

def test_dashboard_stale_flag_and_atomic_anomaly():
    # Insert attendance
    csv_content = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU101,Alice,2026-03-01,10:00,CS101,CS,Present\n"
        "STU102,Bob,2026-03-01,10:00,CS101,CS,Absent\n"
    )
    client.post("/api/attendance/upload", files={"file": ("d1.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")})

    # Check dashboard before running detection: should be stale
    stats_res1 = client.get("/api/dashboard/statistics")
    stats1 = stats_res1.json()
    assert stats1["total_records"] == 2
    assert stats1["analyzed_records"] == 0
    assert stats1["is_stale"] is True

    # Run anomaly detection
    det_res = client.post("/api/anomaly/detect", json={"contamination": 0.1})
    assert det_res.status_code == 200

    # Check dashboard: should be up to date
    stats_res2 = client.get("/api/dashboard/statistics")
    stats2 = stats_res2.json()
    assert stats2["total_records"] == 2
    assert stats2["analyzed_records"] == 2
    assert stats2["is_stale"] is False

    # Upload another record
    new_csv = (
        "student_id,student_name,date,time,subject_code,subject_name,status\n"
        "STU103,Charlie,2026-03-02,10:00,CS101,CS,Present\n"
    )
    client.post("/api/attendance/upload", files={"file": ("d2.csv", io.BytesIO(new_csv.encode("utf-8")), "text/csv")})

    # Dashboard should now be stale again
    stats_res3 = client.get("/api/dashboard/statistics")
    stats3 = stats_res3.json()
    assert stats3["total_records"] == 3
    assert stats3["analyzed_records"] == 2
    assert stats3["is_stale"] is True
