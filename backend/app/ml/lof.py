import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from app.ml.feature_engineering import FEATURE_COLUMNS

def predict_local_outlier_factor(df: pd.DataFrame, contamination: float = 0.10, n_neighbors: int = 20):
    """
    Applies Local Outlier Factor (LOF) on feature columns for comparison with Isolation Forest.
    
    Small-Dataset Handling:
    -----------------------
    LOF measures relative local density compared to k nearest neighbors.
    For N < 3, neighborhood density estimation is mathematically degenerate.
    When N < 3, LOF gracefully returns fallback inlier predictions (Normal, score=0.0)
    with a documented note that sample size is insufficient for density estimation.
    For N >= 3, effective_neighbors is capped at min(n_neighbors, n_samples - 1),
    guaranteeing n_neighbors < n_samples.
    
    Score Formulation:
    ------------------
    LOF produces raw factor >= 0, where ~1.0 indicates normal density and > 1.5 indicates outlier.
    We convert this monotonically to a bounded [0.0, 1.0] index via:
        score = 1.0 - (1.0 / max(1.0, lof_factor))
    - LOF <= 1.0 -> 0.0 (Normal)
    - LOF = 2.0 -> 0.5
    - LOF = 5.0 -> 0.8
    Higher scores indicate stronger density-based outliers.
    
    Returns df with added columns:
      'lof_anomaly_score', 'lof_prediction', 'lof_status', 'lof_is_anomaly'
    """
    df = df.copy()
    n_samples = len(df)
    
    if n_samples == 0:
        df['lof_anomaly_score'] = pd.Series(dtype=float)
        df['lof_prediction'] = pd.Series(dtype=int)
        df['lof_status'] = pd.Series(dtype=str)
        df['lof_is_anomaly'] = pd.Series(dtype=bool)
        return df, None
        
    if n_samples < 3:
        # Insufficient samples for meaningful local density neighborhood
        df['lof_anomaly_score'] = 0.0
        df['lof_prediction'] = 1
        df['lof_status'] = "Normal"
        df['lof_is_anomaly'] = False
        return df, None

    # Guarantee effective_neighbors < n_samples (at most n_samples - 1)
    effective_neighbors = min(n_neighbors, n_samples - 1)
    effective_neighbors = max(1, effective_neighbors)
    
    X = df[FEATURE_COLUMNS].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if isinstance(contamination, (int, float)):
        eff_contamination = min(0.5, max(0.01, float(contamination)))
    else:
        eff_contamination = 0.10
        
    lof = LocalOutlierFactor(
        n_neighbors=effective_neighbors,
        contamination=eff_contamination,
        n_jobs=-1
    )
    
    preds = lof.fit_predict(X_scaled)  # 1 = normal, -1 = anomaly
    raw_factors = -lof.negative_outlier_factor_  # ~1.0 normal, > 1.5 outlier
    
    # Bounded mapping: 1 - 1/max(1.0, factor) in [0.0, 1.0]
    safe_factors = np.maximum(1.0, np.nan_to_num(raw_factors, nan=1.0, posinf=100.0, neginf=1.0))
    normalized_scores = np.clip(1.0 - (1.0 / safe_factors), 0.0, 1.0)
    
    statuses = []
    is_anomalies = []
    
    for pred, norm_score in zip(preds, normalized_scores):
        if pred == -1:
            is_anomalies.append(True)
            if norm_score >= 0.60:
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
