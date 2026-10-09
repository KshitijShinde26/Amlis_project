import pandas as pd
import numpy as np

def extract_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes numerical features for Machine Learning model.
    Does not mutate raw columns; attaches feature columns.
    """
    df = df.copy()
    
    # 1. Overall Student Attendance Percentage
    student_total = df.groupby('student_id')['status_numeric'].transform('count')
    student_presents = df.groupby('student_id')['status_numeric'].transform('sum')
    df['student_overall_pct'] = np.where(student_total > 0, (student_presents / student_total) * 100.0, 0.0)

    # 2. Subject Specific Attendance Percentage for Student
    sub_total = df.groupby(['student_id', 'subject_code'])['status_numeric'].transform('count')
    sub_presents = df.groupby(['student_id', 'subject_code'])['status_numeric'].transform('sum')
    df['student_subject_pct'] = np.where(sub_total > 0, (sub_presents / sub_total) * 100.0, 0.0)

    # 3. Subject Class Average Attendance Percentage
    class_sub_total = df.groupby('subject_code')['status_numeric'].transform('count')
    class_sub_presents = df.groupby('subject_code')['status_numeric'].transform('sum')
    df['class_subject_avg_pct'] = np.where(class_sub_total > 0, (class_sub_presents / class_sub_total) * 100.0, 0.0)

    # 4. Subject Deviation (Student's overall attendance % vs student's attendance % in this subject)
    df['subject_deviation'] = df['student_overall_pct'] - df['student_subject_pct']

    # 5. Class Deviation (Student's subject attendance % vs overall class average in this subject)
    df['class_deviation'] = df['class_subject_avg_pct'] - df['student_subject_pct']

    # 6. Consecutive Absences & Presents Streak (Rolling per student)
    consec_abs = []
    consec_pres = []

    for _, group in df.groupby('student_id', sort=False):
        curr_abs = 0
        curr_pres = 0
        for stat in group['status_numeric']:
            if stat == 0:
                curr_abs += 1
                curr_pres = 0
            else:
                curr_pres += 1
                curr_abs = 0
            consec_abs.append(curr_abs)
            consec_pres.append(curr_pres)

    df['consecutive_absences'] = consec_abs
    df['consecutive_presents'] = consec_pres

    # 7. Recent 5 Classes Moving Average Attendance Rate
    recent_5_pct = []
    for _, group in df.groupby('student_id', sort=False):
        rolling_mean = group['status_numeric'].rolling(window=5, min_periods=1).mean() * 100.0
        recent_5_pct.extend(rolling_mean.tolist())

    df['recent_5_pct'] = recent_5_pct

    # 8. Attendance Rate Shift (Overall % - Recent 5 %)
    df['recent_trend_shift'] = df['student_overall_pct'] - df['recent_5_pct']

    # 9. Unusual Lecture Hour Indicator (Lectures outside 8 AM to 6 PM)
    df['unusual_hour_flag'] = df['hour'].apply(lambda h: 1 if (h < 8 or h >= 18) else 0)

    # 10. Same Date & Time Multiple Presence Flag (Potential Proxy / Duplicate conflict)
    # Check if student is marked Present in multiple subjects at exact same date & time
    presents_df = df[df['status_numeric'] == 1]
    same_time_counts = presents_df.groupby(['student_id', 'attendance_date', 'attendance_time'])['subject_code'].transform('count')
    
    # Map back to full df
    df['time_conflict_flag'] = 0
    df.loc[presents_df.index, 'time_conflict_flag'] = (same_time_counts > 1).astype(int)

    return df

FEATURE_COLUMNS = [
    'status_numeric',
    'hour',
    'day_of_week',
    'student_overall_pct',
    'student_subject_pct',
    'class_subject_avg_pct',
    'subject_deviation',
    'class_deviation',
    'consecutive_absences',
    'recent_5_pct',
    'recent_trend_shift',
    'unusual_hour_flag',
    'time_conflict_flag'
]
