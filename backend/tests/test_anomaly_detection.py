import pytest
import pandas as pd
import numpy as np
from app.ml.isolation_forest import train_and_predict_isolation_forest
from app.ml.lof import predict_local_outlier_factor
from app.ml.feature_engineering import FEATURE_COLUMNS

@pytest.fixture
def dummy_feature_df():
    # Create 50 normal records and 2 extreme anomalies
    np.random.seed(42)
    data = {}
    for col in FEATURE_COLUMNS:
        data[col] = np.random.normal(0, 1, 52)
    
    # Inject anomalies at the end
    for col in FEATURE_COLUMNS:
        data[col][-2:] = [10.0, -10.0]
        
    return pd.DataFrame(data)

def test_isolation_forest(dummy_feature_df):
    df_result, model = train_and_predict_isolation_forest(dummy_feature_df, contamination=0.05)
    
    assert 'if_anomaly_score' in df_result.columns
    assert 'if_prediction' in df_result.columns
    assert 'if_status' in df_result.columns
    assert 'is_anomaly' in df_result.columns
    
    # Last two should likely be flagged as anomalies
    assert df_result['is_anomaly'].iloc[-1] == True
    assert df_result['is_anomaly'].iloc[-2] == True

def test_local_outlier_factor(dummy_feature_df):
    df_result, model = predict_local_outlier_factor(dummy_feature_df, contamination=0.05)
    
    assert 'lof_anomaly_score' in df_result.columns
    assert 'lof_prediction' in df_result.columns
    assert 'lof_status' in df_result.columns
    assert 'lof_is_anomaly' in df_result.columns
    
    # Last two should likely be flagged as anomalies
    assert df_result['lof_is_anomaly'].iloc[-1] == True
    assert df_result['lof_is_anomaly'].iloc[-2] == True
