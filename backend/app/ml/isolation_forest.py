import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.ml.feature_engineering import FEATURE_COLUMNS

def train_and_predict_isolation_forest(df: pd.DataFrame, contamination: float = 0.10):
    """
    Trains Isolation Forest on feature columns and generates anomaly scores & statuses.
    Returns df with added columns: 'if_anomaly_score', 'if_prediction', 'if_status', 'is_anomaly'
    """
    df = df.copy()
    
    X = df[FEATURE_COLUMNS].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_scaled)
    preds = model.predict(X_scaled) # 1 = normal, -1 = anomaly
    dec_scores = model.decision_function(X_scaled) # negative = anomaly, positive = normal
    
    # Normalize decision scores to a user-friendly anomaly index [0.0, 1.0]
    # In decision_function, lower score means more anomalous.
    min_score = dec_scores.min()
    max_score = dec_scores.max()
    score_range = max_score - min_score if max_score != min_score else 1.0
    
    # Invert so 0.0 = Normal, 1.0 = Highly Anomalous
    normalized_scores = 1.0 - ((dec_scores - min_score) / score_range)
    
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
            
    df['if_anomaly_score'] = np.round(normalized_scores, 4)
    df['if_prediction'] = preds
    df['if_status'] = statuses
    df['is_anomaly'] = is_anomalies
    
    return df, model
