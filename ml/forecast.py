
import pandas as pd
from db.init import SessionLocal
from db.models import VMMetric
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

def forecast_cpu(vm_id, hours=24):
    db = SessionLocal()
    try:
        metrics = db.query(VMMetric).filter(VMMetric.vm_id == vm_id).order_by(VMMetric.timestamp).all()
        if len(metrics) < 10:
            return []

        # Simple linear regression without pandas
        cpu_values = [m.cpu_usage for m in metrics]
        time_indices = list(range(len(cpu_values)))
        
        # Convert to numpy arrays
        X = np.array(time_indices).reshape(-1, 1)
        y = np.array(cpu_values)

        model = LinearRegression()
        model.fit(X, y)

        # Predict future values
        future_times = np.arange(len(cpu_values), len(cpu_values) + hours).reshape(-1, 1)
        forecast = model.predict(future_times)

        return forecast.tolist()
    finally:
        db.close()
