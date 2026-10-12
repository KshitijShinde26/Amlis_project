import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.ml.feature_engineering import FEATURE_COLUMNS

def train_and_predict_isolation_forest(df: pd.DataFrame, contamination: float = 0.10):
    """
    Trains Isolation Forest on feature columns and generates anomaly scores & statuses.
    
    Score Formulation:
    ------------------
    Computes standard Isolation Forest structural anomaly score (Liu et al., 2008):
        s(x) = -score_samples(x) = 2^(-E(h(x))/c(n))
    Mathematically bounded in [0.0, 1.0].
    Higher scores indicate greater isolation / outlier severity:
      - s < 0.50: Inlier / typical attendance behavior.
      - s ~= 0.50: Indistinguishable / homogeneous baseline.
      - s > -offset_: Flagged outlier according to the contamination rate.
      
    Note: The anomaly score is an uncalibrated tree isolation depth score,
    not a calibrated posterior probability.
    
    Classification:
    ---------------
    Classification is based strictly on IsolationForest.predict(X) == -1,
    respecting the configured contamination rate rather than an arbitrary
    batch-relative MinMax threshold.
    
    Severity Classification (for flagged anomalies):
      - If pred == -1 and score >= 0.60: "Highly Suspicious"
      - If pred == -1 and score < 0.60: "Suspicious"
      - If pred == 1: "Normal"
    
    Returns df with added columns:
      'if_anomaly_score', 'if_prediction', 'if_status', 'is_anomaly'
    """
    df = df.copy()
    
    if len(df) == 0:
        df['if_anomaly_score'] = pd.Series(dtype=float)
        df['if_prediction'] = pd.Series(dtype=int)
        df['if_status'] = pd.Series(dtype=str)
        df['is_anomaly'] = pd.Series(dtype=bool)
        return df, None

    X = df[FEATURE_COLUMNS].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Ensure contamination is in valid range (0, 0.5] or 'auto'
    if isinstance(contamination, (int, float)):
        eff_contamination = min(0.5, max(0.01, float(contamination)))
    else:
        eff_contamination = 0.10
        
    model = IsolationForest(
        n_estimators=100,
        contamination=eff_contamination,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_scaled)
    preds = model.predict(X_scaled)  # 1 = normal, -1 = anomaly
    
    # Standard Liu et al. (2008) anomaly score: -score_samples(X) in [0.0, 1.0]
    raw_scores = -model.score_samples(X_scaled)
    
    # Ensure scores are strictly finite and bounded in [0.0, 1.0]
    finite_scores = np.nan_to_num(raw_scores, nan=0.5, posinf=1.0, neginf=0.0)
    bounded_scores = np.clip(finite_scores, 0.0, 1.0)
    
    statuses = []
    is_anomalies = []
    
    for pred, score in zip(preds, bounded_scores):
        if pred == -1:
            is_anomalies.append(True)
            if score >= 0.60:
                statuses.append("Highly Suspicious")
            else:
                statuses.append("Suspicious")
        else:
            is_anomalies.append(False)
            statuses.append("Normal")
            
    df['if_anomaly_score'] = np.round(bounded_scores, 4)
    df['if_prediction'] = preds
    df['if_status'] = statuses
    df['is_anomaly'] = is_anomalies
    
    return df, model
