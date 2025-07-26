
from ml.forecast import forecast_cpu
from ml.anomaly import detect_anomalies

def test_forecast_returns_list():
    forecast = forecast_cpu(vm_id=1, hours=5)
    assert isinstance(forecast, list) or forecast == []

def test_anomalies_returns_dicts():
    anomalies = detect_anomalies(vm_id=1)
    assert isinstance(anomalies, list)
    if anomalies:
        assert isinstance(anomalies[0], dict)
