import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import settings
from app.database.init_db import init_db
from app.api import attendance, anomaly, students, subjects, dashboard, reports

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Backend REST API for Smart Attendance Anomaly Detection using Machine Learning (Isolation Forest & LOF)."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(attendance.router, prefix=settings.API_V1_STR)
app.include_router(anomaly.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(subjects.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    init_db()
    print("Database tables initialized successfully.")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database": settings.DATABASE_URL.split(":///")[0]
    }

@app.get("/api/dataset/sample")
def download_sample_dataset():
    sample_file = "dataset/sample_attendance.csv"
    if os.path.exists(sample_file):
        return FileResponse(
            path=sample_file,
            filename="sample_attendance.csv",
            media_type="text/csv"
        )
    return {"error": "Sample dataset file not found."}
