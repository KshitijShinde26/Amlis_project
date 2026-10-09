import time
import pandas as pd
import numpy as np
from app.ml.preprocessing import validate_and_preprocess_dataframe
from app.ml.feature_engineering import extract_ml_features
from app.ml.isolation_forest import train_and_predict_isolation_forest
from app.ml.lof import predict_local_outlier_factor
from app.ml.explainability import generate_reason_indicators

def run_anomaly_pipeline(raw_df: pd.DataFrame, contamination: float = 0.10):
    """
    Executes end-to-end ML anomaly detection pipeline.
    
    Returns:
    - processed_df: Full DataFrame with features, scores, predictions, and reason indicators
    - summary_metrics: Dictionary of execution time, anomaly counts, IF vs LOF comparison stats
    """
    start_time = time.time()
    
    # Step 1: Preprocess & Clean
    cleaned_df = validate_and_preprocess_dataframe(raw_df)
    
    # Step 2: Extract ML Features
    featured_df = extract_ml_features(cleaned_df)
    
    # Step 3: Train & Predict Isolation Forest (Primary Model)
    if_start = time.time()
    df_result, if_model = train_and_predict_isolation_forest(featured_df, contamination=contamination)
    if_time = time.time() - if_start
    
    # Step 4: Predict Local Outlier Factor (Secondary Comparison Model)
    lof_start = time.time()
    df_result, lof_model = predict_local_outlier_factor(df_result, contamination=contamination)
    lof_time = time.time() - lof_start
    
    # Step 5: Generate Explainable Reason Indicators
    reasons = []
    for idx, row in df_result.iterrows():
        r_str = generate_reason_indicators(row)
        reasons.append(r_str)
    df_result['reason_indicators'] = reasons
    
    total_time = time.time() - start_time
    
    # Compute Comparison & Summary Statistics
    total_records = len(df_result)
    if_anomalies_count = int((df_result['if_status'] != 'Normal').sum())
    lof_anomalies_count = int((df_result['lof_status'] != 'Normal').sum())
    
    # Both models agree
    agreed_anomalies = int(((df_result['if_status'] != 'Normal') & (df_result['lof_status'] != 'Normal')).sum())
    
    summary_metrics = {
        "total_records": total_records,
        "isolation_forest": {
            "anomalies_detected": if_anomalies_count,
            "anomaly_percentage": round((if_anomalies_count / total_records * 100.0) if total_records > 0 else 0.0, 2),
            "execution_time_seconds": round(if_time, 4)
        },
        "local_outlier_factor": {
            "anomalies_detected": lof_anomalies_count,
            "anomaly_percentage": round((lof_anomalies_count / total_records * 100.0) if total_records > 0 else 0.0, 2),
            "execution_time_seconds": round(lof_time, 4)
        },
        "model_agreement_count": agreed_anomalies,
        "total_pipeline_time_seconds": round(total_time, 4)
    }
    
    return df_result, summary_metrics
