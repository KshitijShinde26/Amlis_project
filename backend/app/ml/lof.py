import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from app.ml.feature_engineering import FEATURE_COLUMNS

def predict_local_outlier_factor(df: pd.DataFrame, contamination: float = 0.10, n_neighbors: int = 20):
    """
    Applies Local Outlier Factor (LOF) on feature columns for comparison with Isolation Forest.
    Returns df with added columns: 'lof_anomaly_score', 'lof_prediction', 'lof_status', 'lof_is_anomaly'
    """
    df = df.copy()
    
    # Handle small datasets gracefully
    n_samples = len(df)
    effective_neighbors = min(n_neighbors, max(2, n_samples - 1))
    
    X = df[FEATURE_COLUMNS].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    lof = LocalOutlierFactor(
        n_neighbors=effective_neighbors,
        contamination=contamination,
        n_jobs=-1
    )
    
    preds = lof.fit_predict(X_scaled) # 1 = normal, -1 = anomaly
    lof_scores = -lof.negative_outlier_factor_ # Higher value = more anomalous (1.0 is normal, > 1.5 is outlier)
    
    min_score = lof_scores.min()
    max_score = lof_scores.max()
    score_range = max_score - min_score if max_score != min_score else 1.0
    
    normalized_scores = (lof_scores - min_score) / score_range
    
    statuses = []
    is_anomalies = []
    
    for pred, norm_score in zip(preds, normalized_scores):
        if pred == -1 or norm_score >= 0.65:
            is_anomalies.append(True)
            if norm_score >= 0.78:
                statuses.append("Highly Suspicious")
            else:
                statuses.append("Suspicious")
        else:
            is_anomalies.append(False)
            statuses.append("Normal")
            
    df['lof_anomaly_score'] = np.round(normalized_scores, 4)
    df['lof_prediction'] = preds
    df['lof_status'] = statuses
    df['lof_is_anomaly'] = is_anomalies
    
    return df, lof
