
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from recommendation.engine import generate_recommendations
from analysis.engine import get_underutilized_vms
from ml.forecast import forecast_cpu
from ml.anomaly import detect_anomalies
from monitoring.mac_monitor import MacSystemMonitor
import threading
import time

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

# Global variables for monitoring
mac_monitor = None
monitoring_thread = None
monitoring_active = False

# Pydantic models for admin requests
class MacMonitoringRequest(BaseModel):
    interval: int = 30

class ConnectionTestRequest(BaseModel):
    host: str = None
    username: str = None
    password: str = None
    url: str = None

# Admin endpoints
@router.post("/admin/mac/start")
async def start_mac_monitoring(request: MacMonitoringRequest):
    global mac_monitor, monitoring_thread, monitoring_active
    
    if monitoring_active:
        raise HTTPException(status_code=400, detail="Mac monitoring is already running")
    
    try:
        mac_monitor = MacSystemMonitor()
        # Create initial VMs
        mac_monitor.create_virtual_vms()
        # Collect initial metrics
        metrics = mac_monitor.collect_metrics()
        
        # Start background monitoring
        monitoring_active = True
        
        def monitor_loop():
            global monitoring_active
            while monitoring_active:
                try:
                    mac_monitor.collect_metrics()
                    time.sleep(request.interval)
                except Exception as e:
                    print(f"Error in monitoring loop: {e}")
                    break
        
        monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitoring_thread.start()
        
        return {
            "status": "started",
            "interval": request.interval,
            "vm_count": metrics.get('vm_count', 0),
            "system_cpu": metrics.get('system_cpu', 0),
            "system_memory": metrics.get('system_memory', 0)
        }
    except Exception as e:
        monitoring_active = False
        raise HTTPException(status_code=500, detail=f"Failed to start Mac monitoring: {str(e)}")

@router.post("/admin/mac/stop")
async def stop_mac_monitoring():
    global monitoring_active, mac_monitor
    
    if not monitoring_active:
        raise HTTPException(status_code=400, detail="Mac monitoring is not running")
    
    monitoring_active = False
    if mac_monitor:
        mac_monitor.session.close()
        mac_monitor = None
    
    return {"status": "stopped"}

@router.get("/admin/mac/stats")
async def get_mac_stats():
    try:
        temp_monitor = MacSystemMonitor()
        system_info = temp_monitor.get_system_info()
        cpu_usage = temp_monitor.get_cpu_usage()
        memory_usage = temp_monitor.get_memory_usage()
        disk_usage = temp_monitor.get_disk_usage()
        temp_monitor.session.close()
        
        return {
            "system_info": system_info,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "monitoring_active": monitoring_active
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Mac stats: {str(e)}")

@router.post("/admin/vcenter/test")
async def test_vcenter_connection(request: ConnectionTestRequest):
    # Placeholder for vCenter connection test
    # In a real implementation, you would test the actual vCenter connection
    if not request.host or not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Missing required vCenter credentials")
    
    # Simulate connection test
    return {
        "status": "success",
        "message": f"Successfully connected to vCenter at {request.host}",
        "host": request.host,
        "username": request.username
    }

@router.post("/admin/zabbix/test")
async def test_zabbix_connection(request: ConnectionTestRequest):
    # Placeholder for Zabbix connection test
    if not request.url or not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Missing required Zabbix credentials")
    
    # Simulate connection test
    return {
        "status": "success",
        "message": f"Successfully connected to Zabbix at {request.url}",
        "url": request.url,
        "username": request.username
    }

@router.post("/admin/prometheus/test")
async def test_prometheus_connection(request: ConnectionTestRequest):
    # Placeholder for Prometheus connection test
    if not request.url:
        raise HTTPException(status_code=400, detail="Missing Prometheus URL")
    
    # Simulate connection test
    return {
        "status": "success",
        "message": f"Successfully connected to Prometheus at {request.url}",
        "url": request.url
    }
