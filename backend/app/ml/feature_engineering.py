import pandas as pd
import numpy as np

def extract_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes numerical features for Machine Learning model.
    Does not mutate raw columns; attaches feature columns.
    Preserves original DataFrame row order and index alignment.
    """
    df = df.copy()
    
    if df.empty:
        for col in FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = pd.Series(dtype=float)
        return df

    # Ensure status_numeric exists
    if 'status_numeric' not in df.columns:
        if 'status' in df.columns:
            df['status_numeric'] = df['status'].apply(
                lambda val: 1 if str(val).strip().lower() in ['p', 'present', '1', 'true', 'yes'] else 0
            )
        else:
            df['status_numeric'] = 1

    # Ensure hour and day_of_week exist
    if 'hour' not in df.columns:
        df['hour'] = 10
    if 'day_of_week' not in df.columns:
        df['day_of_week'] = 0

    # Ensure subject_code exists
    if 'subject_code' not in df.columns:
        df['subject_code'] = 'GEN101'
    else:
        df['subject_code'] = df['subject_code'].fillna('GEN101').astype(str).str.strip()

    # 1. Overall Student Attendance Percentage (Index-aligned)
    student_total = df.groupby('student_id')['status_numeric'].transform('count')
    student_presents = df.groupby('student_id')['status_numeric'].transform('sum')
    df['student_overall_pct'] = np.where(student_total > 0, (student_presents / student_total) * 100.0, 0.0)

    # 2. Subject Specific Attendance Percentage for Student (Index-aligned)
    sub_total = df.groupby(['student_id', 'subject_code'])['status_numeric'].transform('count')
    sub_presents = df.groupby(['student_id', 'subject_code'])['status_numeric'].transform('sum')
    df['student_subject_pct'] = np.where(sub_total > 0, (sub_presents / sub_total) * 100.0, 0.0)

    # 3. Subject Class Average Attendance Percentage (Index-aligned)
    class_sub_total = df.groupby('subject_code')['status_numeric'].transform('count')
    class_sub_presents = df.groupby('subject_code')['status_numeric'].transform('sum')
    df['class_subject_avg_pct'] = np.where(class_sub_total > 0, (class_sub_presents / class_sub_total) * 100.0, 0.0)

    # 4. Subject Deviation (Student's overall attendance % vs student's attendance % in this subject)
    df['subject_deviation'] = df['student_overall_pct'] - df['student_subject_pct']

    # 5. Class Deviation (Student's subject attendance % vs overall class average in this subject)
    df['class_deviation'] = df['class_subject_avg_pct'] - df['student_subject_pct']

    # --- Chronological Sequential Feature Calculation ---
    # Determine date and time sorting keys
    date_col = None
    for candidate in ['attendance_date', 'date']:
        if candidate in df.columns:
            date_col = candidate
            break

    time_col = None
    for candidate in ['attendance_time', 'time']:
        if candidate in df.columns:
            time_col = candidate
            break

    # Build sorting DataFrame that includes original row position for stable tie-breaking
    # on simultaneous records (records with exact same date and time)
    df['_orig_order'] = np.arange(len(df))
    sort_cols = ['student_id']
    if date_col:
        sort_cols.append(date_col)
    if time_col:
        sort_cols.append(time_col)
    sort_cols.append('_orig_order')

    df_sorted = df.sort_values(by=sort_cols, kind='mergesort')

    # 6. Consecutive Absences & Presents Streak (Rolling per student, strictly historical)
    streak_records = []
    for _, group in df_sorted.groupby('student_id', sort=False):
        c_abs = 0
        c_pres = 0
        for idx, val in zip(group.index, group['status_numeric']):
            if val == 0:
                c_abs += 1
                c_pres = 0
            else:
                c_pres += 1
                c_abs = 0
            streak_records.append((idx, c_abs, c_pres))

    if streak_records:
        streak_df = pd.DataFrame(streak_records, columns=['idx', 'consec_abs', 'consec_pres']).set_index('idx')
        df['consecutive_absences'] = streak_df['consec_abs']
        df['consecutive_presents'] = streak_df['consec_pres']
    else:
        df['consecutive_absences'] = 0
        df['consecutive_presents'] = 0

    # 7. Recent 5 Classes Moving Average Attendance Rate (Past-looking only, window=5)
    recent_5_records = []
    for _, group in df_sorted.groupby('student_id', sort=False):
        rolling_mean = group['status_numeric'].rolling(window=5, min_periods=1).mean() * 100.0
        for idx, val in zip(group.index, rolling_mean):
            recent_5_records.append((idx, val))

    if recent_5_records:
        recent_df = pd.DataFrame(recent_5_records, columns=['idx', 'recent_5_pct']).set_index('idx')
        df['recent_5_pct'] = recent_df['recent_5_pct']
    else:
        df['recent_5_pct'] = 0.0

    # Clean up temporary ordering column
    df.drop(columns=['_orig_order'], inplace=True, errors='ignore')

    # 8. Attendance Rate Shift (Overall % - Recent 5 %)
    df['recent_trend_shift'] = df['student_overall_pct'] - df['recent_5_pct']

    # 9. Unusual Lecture Hour Indicator (Lectures outside 8 AM to 6 PM)
    df['unusual_hour_flag'] = df['hour'].apply(lambda h: 1 if (h < 8 or h >= 18) else 0)

    # 10. Same Date & Time Multiple Presence Flag (Potential Proxy / Duplicate conflict)
    # Check if student is marked Present in multiple subjects at exact same date & time
    presents_df = df[df['status_numeric'] == 1]
    if not presents_df.empty and date_col and time_col:
        same_time_counts = presents_df.groupby(['student_id', date_col, time_col])['subject_code'].transform('count')
        df['time_conflict_flag'] = 0
        df.loc[presents_df.index, 'time_conflict_flag'] = (same_time_counts > 1).astype(int)
    else:
        df['time_conflict_flag'] = 0

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
