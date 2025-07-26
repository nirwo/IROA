
from fastapi import APIRouter
from recommendation.engine import generate_recommendations
from analysis.engine import get_underutilized_vms
from ml.forecast import forecast_cpu
from ml.anomaly import detect_anomalies

router = APIRouter()

@router.get("/recommendations")
def list_recommendations():
    return generate_recommendations()

@router.get("/underutilized")
def list_underutilized():
    return get_underutilized_vms()

@router.get("/forecast/{vm_id}")
def forecast_vm(vm_id: int, hours: int = 24):
    return {"vm_id": vm_id, "forecast_hours": hours, "cpu_forecast": forecast_cpu(vm_id, hours)}

@router.get("/anomalies/{vm_id}")
def anomalies_vm(vm_id: int):
    return {"vm_id": vm_id, "anomalies": detect_anomalies(vm_id)}
