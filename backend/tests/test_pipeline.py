import pytest
import pandas as pd
from app.ml.pipeline import run_anomaly_pipeline

def test_run_anomaly_pipeline():
    data = {
        'student_id': [f'S{i}' for i in range(20)],
        'date': ['2023-10-01'] * 20,
        'time': ['10:00'] * 20,
        'status': ['Present'] * 18 + ['Absent'] * 2,
        'subject_code': ['CS101'] * 20
    }
    raw_df = pd.DataFrame(data)
    
    df_result, summary_metrics = run_anomaly_pipeline(raw_df, contamination=0.1)
    
    # Check outputs
    assert 'reason_indicators' in df_result.columns
    assert 'if_status' in df_result.columns
    assert 'lof_status' in df_result.columns
    
    assert summary_metrics['total_records'] == 20
    assert 'isolation_forest' in summary_metrics
    assert 'local_outlier_factor' in summary_metrics
    
    # Ensure anomalies detected is integer
    assert isinstance(summary_metrics['isolation_forest']['anomalies_detected'], int)

@pytest.mark.parametrize("n", [1, 2, 5])
def test_pipeline_small_datasets_n1_n2_n5(n):
    data = {
        'student_id': [f'S{i}' for i in range(n)],
        'date': ['2023-10-01'] * n,
        'time': ['10:00'] * n,
        'status': ['Present'] * n,
        'subject_code': ['CS101'] * n
    }
    raw_df = pd.DataFrame(data)
    
    df_result, summary_metrics = run_anomaly_pipeline(raw_df, contamination=0.1)
    
    assert len(df_result) == n
    assert summary_metrics['total_records'] == n
    assert 'isolation_forest' in summary_metrics
    assert 'local_outlier_factor' in summary_metrics
    
    # Check that scores are finite and within [0, 1]
    assert (df_result['if_anomaly_score'] >= 0.0).all() and (df_result['if_anomaly_score'] <= 1.0).all()
    assert (df_result['lof_anomaly_score'] >= 0.0).all() and (df_result['lof_anomaly_score'] <= 1.0).all()
    
    # Prediction and status columns must be populated
    assert 'if_status' in df_result.columns
    assert 'lof_status' in df_result.columns

