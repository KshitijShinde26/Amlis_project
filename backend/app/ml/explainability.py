import json
import pandas as pd

def generate_reason_indicators(row: pd.Series) -> str:
    """
    Analyzes row feature metrics to produce human-readable rule-based explanation
    reasons explaining WHY a specific attendance record triggered an anomaly score.
    """
    reasons = []

    # 1. Same-time multi-subject conflict (Potential Proxy / Duplicate log)
    if row.get('time_conflict_flag', 0) == 1:
        reasons.append("Potential Proxy / Duplicate: Student marked Present in multiple subjects at exact same date & time.")

    # 2. Unusual lecture hour
    if row.get('unusual_hour_flag', 0) == 1:
        hour = row.get('hour', 10)
        reasons.append(f"Unusual Timestamp: Attendance logged at irregular hour ({hour:02d}:00), outside standard 08:00–18:00 window.")

    # 3. Consecutive Absence streak
    consec_abs = row.get('consecutive_absences', 0)
    if row.get('status') == 'Absent' and consec_abs >= 3:
        reasons.append(f"Consecutive Absence Streak: Student has been absent for {int(consec_abs)} consecutive classes.")

    # 4. Subject Specific Deviation vs Student Overall
    subj_dev = row.get('subject_deviation', 0)
    if abs(subj_dev) >= 25.0:
        overall = row.get('student_overall_pct', 0)
        subj_pct = row.get('student_subject_pct', 0)
        reasons.append(
            f"Subject Attendance Discrepancy: Attendance in {row.get('subject_code', 'subject')} ({subj_pct:.1f}%) "
            f"deviates significantly from overall attendance rate ({overall:.1f}%)."
        )

    # 5. Class Average Deviation
    class_dev = row.get('class_deviation', 0)
    if class_dev >= 30.0:
        class_avg = row.get('class_subject_avg_pct', 0)
        subj_pct = row.get('student_subject_pct', 0)
        reasons.append(
            f"Outlier vs Peer Group: Student subject attendance ({subj_pct:.1f}%) is substantially lower "
            f"than class average ({class_avg:.1f}%)."
        )

    # 6. Sudden Trend Shift
    shift = row.get('recent_trend_shift', 0)
    if shift >= 30.0:
        overall = row.get('student_overall_pct', 0)
        recent = row.get('recent_5_pct', 0)
        reasons.append(
            f"Sudden Attendance Drop: Recent 5-class attendance rate ({recent:.1f}%) dropped sharply "
            f"compared to overall baseline ({overall:.1f}%)."
        )

    # Fallback if model flagged it but no single rule exceeded high threshold
    if not reasons:
        if row.get('if_status') != 'Normal' or row.get('lof_status') != 'Normal':
            reasons.append("Multivariate Pattern Outlier: Combined behavioral features deviate significantly from normal historical distribution.")

    return json.dumps(reasons)
