import pytest
import pandas as pd
from app.ml.preprocessing import validate_and_preprocess_dataframe

def test_preprocessing_valid_data():
    data = {
        'student_id': ['1', '2'],
        'date': ['2023-10-01', '2023-10-02'],
        'time': ['10:00', '14:30'],
        'status': ['Present', 'Absent']
    }
    df = pd.DataFrame(data)
    result = validate_and_preprocess_dataframe(df)
    
    assert 'attendance_date' in result.columns
    assert 'hour' in result.columns
    assert 'status_numeric' in result.columns
    assert result['hour'].tolist() == [10, 14]
    assert result['status_numeric'].tolist() == [1, 0]
    assert result['subject_code'].tolist() == ['GEN101', 'GEN101']

def test_preprocessing_missing_mandatory_cols():
    df = pd.DataFrame({'student_id': ['1']})
    with pytest.raises(ValueError, match="Missing mandatory column"):
        validate_and_preprocess_dataframe(df)

def test_preprocessing_invalid_date():
    data = {
        'student_id': ['1'],
        'date': ['invalid_date'],
        'status': ['Present']
    }
    df = pd.DataFrame(data)
    result = validate_and_preprocess_dataframe(df)
    assert len(result) == 0

def test_preprocessing_status_mapping():
    data = {
        'student_id': ['1', '2', '3', '4'],
        'date': ['2023-10-01', '2023-10-01', '2023-10-01', '2023-10-01'],
        'status': ['P', 'present', 'A', 'absent']
    }
    df = pd.DataFrame(data)
    result = validate_and_preprocess_dataframe(df)
    assert result['status_numeric'].tolist() == [1, 1, 0, 0]
