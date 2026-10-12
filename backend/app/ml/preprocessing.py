import pandas as pd
import numpy as np

def validate_and_preprocess_dataframe(df: pd.DataFrame, return_details: bool = False):
    """
    Validates CSV/Excel columns, cleans missing values, formats date & time.
    Expected columns: student_id, student_name, date, time, subject_code, subject_name, status
    
    If return_details is True, returns (cleaned_df, warnings_list, dropped_records_count).
    If return_details is False, returns cleaned_df for backwards compatibility.
    """
    df = df.copy()
    warnings = []
    
    # Standardize column names (strip whitespace, lowercase)
    col_mapping = {col: str(col).strip().lower() for col in df.columns}
    df = df.rename(columns=col_mapping)
    
    required_cols = ['student_id', 'date', 'status']
    for req in required_cols:
        if req not in df.columns:
            raise ValueError(f"Missing mandatory column: {req}")
            
    # Standardize student_id
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # Standardize student_name
    if 'student_name' not in df.columns or df['student_name'].isnull().all():
        df['student_name'] = df['student_id']
    else:
        df['student_name'] = df['student_name'].fillna('Unknown Student').astype(str).str.strip()
        
    # Standardize subject_code and subject_name
    if 'subject_code' not in df.columns:
        df['subject_code'] = 'GEN101'
    else:
        df['subject_code'] = df['subject_code'].fillna('GEN101').astype(str).str.strip()
        
    if 'subject_name' not in df.columns:
        df['subject_name'] = df['subject_code']
    else:
        df['subject_name'] = df['subject_name'].fillna(df['subject_code']).astype(str).str.strip()

    # Clean date and track invalid date rows
    parsed_dates = pd.to_datetime(df['date'], errors='coerce')
    invalid_date_mask = parsed_dates.isna()
    dropped_count = int(invalid_date_mask.sum())
    
    if dropped_count > 0:
        for idx in df[invalid_date_mask].index:
            raw_val = df.loc[idx, 'date']
            warnings.append(f"Row {idx + 1}: Invalid or unparseable date '{raw_val}' — skipped.")
        df = df[~invalid_date_mask].copy()
        parsed_dates = parsed_dates[~invalid_date_mask]
    
    df['date'] = parsed_dates
    df['attendance_date'] = df['date'].dt.date
    
    # Clean time
    if 'time' not in df.columns or df['time'].isnull().all():
        df['attendance_time'] = "10:00:00"
    else:
        df['attendance_time'] = df['time'].astype(str).str.strip()
        
    # Parse hour & minute
    def parse_hour(time_str):
        try:
            t = pd.to_datetime(str(time_str), format='%H:%M', errors='coerce')
            if pd.isna(t):
                t = pd.to_datetime(str(time_str), format='%H:%M:%S', errors='coerce')
            if pd.isna(t):
                return 10
            return t.hour
        except:
            return 10
            
    df['hour'] = df['attendance_time'].apply(parse_hour)
    df['day_of_week'] = df['date'].dt.dayofweek # 0=Monday, 6=Sunday

    # Clean Status (Present, Absent, Late, Excused, Medical)
    clean_statuses = []
    numeric_statuses = []
    
    for idx, val in zip(df.index, df['status']):
        val_str = str(val).strip().lower()
        if val_str in ['p', 'present', '1', 'true', 'yes']:
            clean_statuses.append('Present')
            numeric_statuses.append(1)
        elif val_str in ['a', 'absent', '0', 'false', 'no']:
            clean_statuses.append('Absent')
            numeric_statuses.append(0)
        elif val_str == 'late':
            clean_statuses.append('Late')
            numeric_statuses.append(1)
        elif val_str in ['excused', 'medical']:
            clean_statuses.append(val_str.capitalize())
            numeric_statuses.append(1)
        else:
            warnings.append(f"Row {idx + 1}: Unrecognized status '{val}' normalized to 'Absent'.")
            clean_statuses.append('Absent')
            numeric_statuses.append(0)
        
    df['status'] = clean_statuses
    df['status_numeric'] = numeric_statuses

    # Sort chronologically by student and date/time
    df = df.sort_values(by=['student_id', 'date', 'attendance_time']).reset_index(drop=True)
    
    if return_details:
        return df, warnings, dropped_count
    return df
