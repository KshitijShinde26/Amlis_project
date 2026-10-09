from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.pydantic_schemas import UploadResponse
from app.services.attendance_service import process_and_save_attendance
from app.models.database import AttendanceRecord

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/upload", response_model=UploadResponse)
async def upload_attendance_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV or Excel attendance dataset.
    Validates dataset structure, populates DB tables, and returns preview summary.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .csv or .xlsx file.")

    contents = await file.read()
    try:
        res = process_and_save_attendance(contents, file.filename, db)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@router.get("")
def get_all_attendance(db: Session = Depends(get_db), limit: int = 100, skip: int = 0):
    records = db.query(AttendanceRecord).offset(skip).limit(limit).all()
    total = db.query(AttendanceRecord).count()
    return {"total": total, "records": records}
