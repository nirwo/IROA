
import pandas as pd
from db.init import SessionLocal
from db.models import VMMetric
from sklearn.ensemble import IsolationForest

def detect_anomalies(vm_id):
    db = SessionLocal()
    try:
        metrics = db.query(VMMetric).filter(VMMetric.vm_id == vm_id).all()
        if len(metrics) < 10:
            return []

        # Extract features without pandas
        features = []
        for m in metrics:
            features.append([m.cpu_usage, m.memory_usage, m.disk_io, m.net_io])
        
        import numpy as np
        X = np.array(features)

        model = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = model.fit_predict(X)

        # Return indices and values of anomalies
        anomalies = []
        for i, label in enumerate(anomaly_labels):
            if label == -1:
                anomalies.append({
                    "index": i,
                    "cpu": features[i][0],
                    "memory": features[i][1],
                    "disk": features[i][2],
                    "net": features[i][3],
                    "timestamp": metrics[i].timestamp.isoformat()
                })
        
        return anomalies
    finally:
        db.close()
