import pytest
import pandas as pd
from app.ml.feature_engineering import extract_ml_features, FEATURE_COLUMNS

def test_extract_ml_features_structure():
    data = {
        'student_id': ['1', '1', '2'],
        'subject_code': ['CS101', 'CS101', 'CS101'],
        'status_numeric': [1, 0, 1],
        'hour': [9, 10, 18],
        'attendance_date': ['2023-10-01', '2023-10-02', '2023-10-01'],
        'attendance_time': ['09:00', '10:00', '18:00'],
        'day_of_week': [0, 1, 0]
    }
    df = pd.DataFrame(data)
    result = extract_ml_features(df)
    
    # Check that all feature columns are generated
    for col in FEATURE_COLUMNS:
        assert col in result.columns

def test_extract_ml_features_logic():
    data = {
        'student_id': ['1', '1', '1', '2', '2'],
        'subject_code': ['CS101', 'CS101', 'CS101', 'CS101', 'CS101'],
        'status_numeric': [1, 0, 1, 0, 0],
        'hour': [10, 10, 20, 10, 10], # 20 is unusual hour
        'attendance_date': ['2023-10-01', '2023-10-02', '2023-10-03', '2023-10-01', '2023-10-02'],
        'attendance_time': ['10:00', '10:00', '20:00', '10:00', '10:00'],
        'day_of_week': [0, 1, 2, 0, 1]
    }
    df = pd.DataFrame(data)
    result = extract_ml_features(df)
    
    # Student 1 has 2/3 present -> ~66.67%
    # Student 2 has 0/2 present -> 0%
    assert abs(result.loc[result['student_id'] == '1', 'student_overall_pct'].iloc[0] - 66.66) < 0.1
    assert result.loc[result['student_id'] == '2', 'student_overall_pct'].iloc[0] == 0.0
    
    # Check unusual hour (Student 1 at 20:00)
    assert result.loc[(result['student_id'] == '1') & (result['hour'] == 20), 'unusual_hour_flag'].iloc[0] == 1

def test_extract_ml_features_time_conflict():
    data = {
        'student_id': ['1', '1'],
        'subject_code': ['CS101', 'MA101'],
        'status_numeric': [1, 1],
        'hour': [10, 10],
        'attendance_date': ['2023-10-01', '2023-10-01'],
        'attendance_time': ['10:00', '10:00'],
        'day_of_week': [0, 0]
    }
    df = pd.DataFrame(data)
    result = extract_ml_features(df)
    
    # Should flag as time conflict
    assert (result['time_conflict_flag'] == 1).all()
