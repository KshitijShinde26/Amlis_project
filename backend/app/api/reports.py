from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import io
from app.database.session import get_db
from app.services.report_service import generate_csv_report, generate_excel_report, generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/anomalies/export")
def export_anomaly_report(
    format: str = Query("csv", description="Format: csv, excel, or pdf"),
    anomaly_only: bool = Query(False, description="Filter for flagged suspicious records only"),
    db: Session = Depends(get_db)
):
    """
    Downloads anomaly detection report in CSV, Excel (.xlsx), or PDF format.
    """
    format = format.lower()
    
    if format == "csv":
        csv_data = generate_csv_report(db, anomaly_only=anomaly_only)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=attendance_anomaly_report.csv"}
        )
        
    elif format in ["excel", "xlsx"]:
        excel_bytes = generate_excel_report(db, anomaly_only=anomaly_only)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=attendance_anomaly_report.xlsx"}
        )
        
    elif format == "pdf":
        pdf_bytes = generate_pdf_report(db, anomaly_only=anomaly_only)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=attendance_anomaly_report.pdf"}
        )
        
    else:
        return Response(
            content=generate_csv_report(db, anomaly_only=anomaly_only),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=attendance_anomaly_report.csv"}
        )
