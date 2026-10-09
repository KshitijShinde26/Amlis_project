from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.pydantic_schemas import DetectionRequest, DetectionResponse
from app.services.anomaly_service import run_database_anomaly_detection, get_anomaly_results_list

router = APIRouter(tags=["Anomaly Detection"])

@router.post("/anomaly/detect", response_model=DetectionResponse)
def trigger_anomaly_detection(req: DetectionRequest = DetectionRequest(), db: Session = Depends(get_db)):
    """
    Triggers the Machine Learning Anomaly Detection pipeline (Isolation Forest + LOF)
    over stored attendance data and saves results.
    """
    res = run_database_anomaly_detection(db, contamination=req.contamination or 0.10)
    return res

@router.get("/anomalies")
def list_anomalies(
    student_id: Optional[str] = None,
    subject_code: Optional[str] = None,
    status_filter: Optional[str] = None,
    anomaly_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieves filtered list of anomaly detection results with explainability indicators.
    """
    results = get_anomaly_results_list(
        db,
        student_id=student_id,
        subject_code=subject_code,
        status_filter=status_filter,
        anomaly_only=anomaly_only
    )
    return {"total": len(results), "results": results}

@router.get("/anomalies/details/{anomaly_id}")
def get_anomaly_detail(anomaly_id: int, db: Session = Depends(get_db)):
    results = get_anomaly_results_list(db)
    target = next((r for r in results if r['id'] == anomaly_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Anomaly record not found")
    return target
