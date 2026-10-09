import os

class Settings:
    APP_NAME: str = "Smart Attendance Anomaly Detection System"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_attendance.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-for-amlis-project")

settings = Settings()
