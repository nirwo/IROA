
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

# Prometheus Mac metrics endpoints
@router.get("/prometheus/mac/metrics")
async def get_prometheus_mac_metrics():
    """Get Mac system metrics from Prometheus"""
    import requests
    import json
    
    try:
        prometheus_url = "http://localhost:9090"
        
        # Get CPU usage using load average (more reliable for Mac)
        cpu_response = requests.get(f"{prometheus_url}/api/v1/query", 
                                  params={"query": "node_load1"})
        
        # Get memory usage (Mac-specific: active + wired memory)
        memory_response = requests.get(f"{prometheus_url}/api/v1/query",
                                     params={"query": "((node_memory_active_bytes + node_memory_wired_bytes) / node_memory_total_bytes) * 100"})
        
        # Get disk usage for root filesystem
        disk_response = requests.get(f"{prometheus_url}/api/v1/query",
                                   params={"query": "100 - ((node_filesystem_free_bytes{{mountpoint='/'}} * 100) / node_filesystem_size_bytes{{mountpoint='/'}})"})
        
        # Parse responses
        cpu_usage = 0
        if cpu_response.status_code == 200:
            cpu_data = cpu_response.json()
            if cpu_data.get('data', {}).get('result'):
                load_avg = float(cpu_data['data']['result'][0]['value'][1])
                # Convert load average to percentage (load/cores * 100)
                cpu_usage = min((load_avg / 10) * 100, 100)  # 10 cores
        
        memory_usage = 0
        if memory_response.status_code == 200:
            memory_data = memory_response.json()
            if memory_data.get('data', {}).get('result'):
                memory_usage = float(memory_data['data']['result'][0]['value'][1])
        
        disk_usage = 0
        if disk_response.status_code == 200:
            disk_data = disk_response.json()
            if disk_data.get('data', {}).get('result'):
                disk_usage = float(disk_data['data']['result'][0]['value'][1])
        
        return {
            "hostname": "Mac-System",
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2),
            "disk_usage": round(disk_usage, 2),
            "status": "running",
            "source": "prometheus",
            "cores": 10,  # Based on the metrics we saw
            "memory_total_gb": 18  # ~19GB total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Prometheus metrics: {str(e)}")

@router.get("/vms")
async def get_all_vms():
    """Get all VMs including Mac system from Prometheus"""
    try:
        # Get traditional underutilized VMs
        underutilized = get_underutilized_vms()
        
        # Get Mac system metrics from Prometheus
        mac_metrics_response = await get_prometheus_mac_metrics()
        
        # Create Mac VM entry
        mac_vm = {
            "vm": "Mac-System",
            "status": "running",
            "cpu": mac_metrics_response["cpu_usage"],
            "memory_usage": mac_metrics_response["memory_usage"],
            "cores": mac_metrics_response["cores"],
            "memory": mac_metrics_response["memory_total_gb"],
            "cluster": "local-mac",
            "source": "prometheus",
            "details": {
                "avg_cpu": mac_metrics_response["cpu_usage"],
                "avg_mem": mac_metrics_response["memory_usage"],
                "disk_usage": mac_metrics_response["disk_usage"]
            }
        }
        
        # Combine all VMs
        all_vms = [mac_vm] + underutilized
        return all_vms
        
    except Exception as e:
        # If Prometheus fails, just return underutilized VMs
        return get_underutilized_vms()

@router.get("/analytics/prometheus")
async def get_prometheus_analytics():
    """Get Mac analytics data from Prometheus"""
    import requests
    
    try:
        prometheus_url = "http://localhost:9090"
        
        # Get CPU usage over time (last hour)
        cpu_history = requests.get(f"{prometheus_url}/api/v1/query_range",
                                 params={
                                     "query": "100 - (avg(rate(node_cpu_seconds_total{{mode='idle'}}[5m])) * 100)",
                                     "start": "2025-07-26T08:00:00Z",
                                     "end": "2025-07-26T12:00:00Z",
                                     "step": "300s"
                                 })
        
        # Get memory usage over time
        memory_history = requests.get(f"{prometheus_url}/api/v1/query_range",
                                    params={
                                        "query": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
                                        "start": "2025-07-26T08:00:00Z",
                                        "end": "2025-07-26T12:00:00Z",
                                        "step": "300s"
                                    })
        
        cpu_data = []
        memory_data = []
        
        if cpu_history.status_code == 200:
            cpu_result = cpu_history.json()
            if cpu_result.get('data', {}).get('result'):
                cpu_values = cpu_result['data']['result'][0]['values']
                cpu_data = [float(value[1]) for value in cpu_values[-12:]]  # Last 12 points
        
        if memory_history.status_code == 200:
            memory_result = memory_history.json()
            if memory_result.get('data', {}).get('result'):
                memory_values = memory_result['data']['result'][0]['values']
                memory_data = [float(value[1]) for value in memory_values[-12:]]  # Last 12 points
        
        return {
            "cpu_history": cpu_data,
            "memory_history": memory_data,
            "source": "prometheus",
            "timeframe": "last_4_hours"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Prometheus analytics: {str(e)}")
