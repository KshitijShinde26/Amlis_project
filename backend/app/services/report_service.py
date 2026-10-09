import io
import json
import pandas as pd
from sqlalchemy.orm import Session
from app.services.anomaly_service import get_anomaly_results_list
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_csv_report(db: Session, anomaly_only: bool = False) -> str:
    results = get_anomaly_results_list(db, anomaly_only=anomaly_only)
    if not results:
        return "Student ID,Student Name,Subject Code,Subject Name,Date,Time,Status,Anomaly Score,Anomaly Status,Reasons\n"

    rows = []
    for r in results:
        reasons_str = "; ".join(r['reason_indicators']) if isinstance(r['reason_indicators'], list) else str(r['reason_indicators'])
        rows.append({
            "Student ID": r['student_id'],
            "Student Name": r['student_name'],
            "Subject Code": r['subject_code'],
            "Subject Name": r['subject_name'],
            "Date": r['attendance_date'],
            "Time": r['attendance_time'],
            "Status": r['attendance_status'],
            "Anomaly Score": r['anomaly_score'],
            "Anomaly Status": r['anomaly_status'],
            "Detection Method": r['detection_method'],
            "Reason Indicators": reasons_str
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def generate_excel_report(db: Session, anomaly_only: bool = False) -> bytes:
    results = get_anomaly_results_list(db, anomaly_only=anomaly_only)
    rows = []
    for r in results:
        reasons_str = "; ".join(r['reason_indicators']) if isinstance(r['reason_indicators'], list) else str(r['reason_indicators'])
        rows.append({
            "Student ID": r['student_id'],
            "Student Name": r['student_name'],
            "Subject Code": r['subject_code'],
            "Subject Name": r['subject_name'],
            "Date": r['attendance_date'],
            "Time": r['attendance_time'],
            "Status": r['attendance_status'],
            "Anomaly Score": r['anomaly_score'],
            "Anomaly Status": r['anomaly_status'],
            "Detection Method": r['detection_method'],
            "Reason Indicators": reasons_str
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Anomaly Report')
    output.seek(0)
    return output.getvalue()

def generate_pdf_report(db: Session, anomaly_only: bool = False) -> bytes:
    results = get_anomaly_results_list(db, anomaly_only=anomaly_only)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'ReportSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )

    story.append(Paragraph("Smart Attendance Anomaly Detection Report", title_style))
    filter_label = "Flagged Suspicious Records Only" if anomaly_only else "All Analyzed Attendance Records"
    story.append(Paragraph(f"Scope: {filter_label} | Generated via ML Isolation Forest Model", subtitle_style))

    table_data = [
        ["Student", "Subject", "Date & Time", "Status", "Score", "Classification", "Reason Indicators"]
    ]

    cell_style = ParagraphStyle('CellText', fontSize=8, leading=10)
    alert_style = ParagraphStyle('AlertCellText', fontSize=8, leading=10, textColor=colors.HexColor('#dc2626'))

    for r in results[:100]: # Top 100 for PDF presentation
        reasons_list = r['reason_indicators'] if isinstance(r['reason_indicators'], list) else [str(r['reason_indicators'])]
        reasons_text = "<br/>• ".join([""] + reasons_list) if reasons_list else "None"
        
        is_suspicious = r['anomaly_status'] != 'Normal'
        curr_cell_style = alert_style if is_suspicious else cell_style

        row = [
            Paragraph(f"<b>{r['student_id']}</b><br/>{r['student_name']}", cell_style),
            Paragraph(f"<b>{r['subject_code']}</b><br/>{r['subject_name']}", cell_style),
            Paragraph(f"{r['attendance_date']}<br/>{r['attendance_time']}", cell_style),
            Paragraph(r['attendance_status'], cell_style),
            Paragraph(f"{r['anomaly_score']:.2f}", cell_style),
            Paragraph(r['anomaly_status'], curr_cell_style),
            Paragraph(reasons_text[:200], cell_style)
        ]
        table_data.append(row)

    t = Table(table_data, colWidths=[80, 85, 75, 50, 45, 80, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))

    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
