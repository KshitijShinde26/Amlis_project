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

def test_identical_normal_records_do_not_receive_false_one():
    # Two identical records (representing homogeneous data)
    data = {col: [0.0, 0.0] for col in FEATURE_COLUMNS}
    df = pd.DataFrame(data)
    
    df_result, model = train_and_predict_isolation_forest(df, contamination=0.1)
    
    # Must NOT receive 1.0 due to zero-range normalization
    assert (df_result['if_anomaly_score'] < 1.0).all()
    assert (df_result['if_anomaly_score'] >= 0.0).all()
    # Identical records should not be classified as Highly Suspicious
    assert (df_result['if_status'] != 'Highly Suspicious').all()

def test_constant_feature_columns_and_nan_stability():
    # 5 identical records with constant and NaN values
    data = {col: [np.nan, 0.0, 0.0, 0.0, 0.0] for col in FEATURE_COLUMNS}
    df = pd.DataFrame(data)
    
    df_if, _ = train_and_predict_isolation_forest(df, contamination=0.1)
    df_lof, _ = predict_local_outlier_factor(df, contamination=0.1)
    
    # Check that scores are finite (no NaN, no inf) and within [0, 1]
    assert np.isfinite(df_if['if_anomaly_score']).all()
    assert (df_if['if_anomaly_score'] >= 0.0).all() and (df_if['if_anomaly_score'] <= 1.0).all()
    
    assert np.isfinite(df_lof['lof_anomaly_score']).all()
    assert (df_lof['lof_anomaly_score'] >= 0.0).all() and (df_lof['lof_anomaly_score'] <= 1.0).all()

def test_anomaly_classification_model_driven():
    # Anomaly classification should strictly follow prediction
    np.random.seed(42)
    data = {col: np.random.normal(0, 1, 30) for col in FEATURE_COLUMNS}
    # Outlier
    for col in FEATURE_COLUMNS:
        data[col][-1] = 20.0
    df = pd.DataFrame(data)
    
    df_result, _ = train_and_predict_isolation_forest(df, contamination=0.1)
    
    # is_anomaly must match if_prediction == -1
    for _, row in df_result.iterrows():
        if row['if_prediction'] == -1:
            assert row['is_anomaly'] == True
            assert row['if_status'] in ['Suspicious', 'Highly Suspicious']
        else:
            assert row['is_anomaly'] == False
            assert row['if_status'] == 'Normal'

