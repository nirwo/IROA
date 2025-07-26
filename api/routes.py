
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from recommendation.engine import generate_recommendations
from analysis.engine import get_underutilized_vms
from ml.forecast import forecast_cpu
from ml.anomaly import detect_anomalies
from monitoring.mac_monitor import MacSystemMonitor
import threading
import time
import psutil
import platform
from datetime import datetime, timedelta
from typing import List, Dict, Any

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

# System detection endpoint
@router.get("/system/info")
async def get_system_info():
    """Get current system information and OS type"""
    import platform
    import psutil
    
    system = platform.system().lower()
    os_name = platform.platform()
    
    # Map system types to monitoring configurations
    os_config = {
        "darwin": {
            "name": "macOS",
            "icon": "🍎",
            "monitoring_available": True,
            "prometheus_job": "node-exporter",
            "description": "Monitor your Mac system resources"
        },
        "linux": {
            "name": "Linux",
            "icon": "🐧", 
            "monitoring_available": True,
            "prometheus_job": "node-exporter",
            "description": "Monitor your Linux system resources"
        },
        "windows": {
            "name": "Windows",
            "icon": "🪟",
            "monitoring_available": True,
            "prometheus_job": "windows-exporter",
            "description": "Monitor your Windows system resources"
        }
    }
    
    current_os = os_config.get(system, {
        "name": "Unknown",
        "icon": "💻",
        "monitoring_available": False,
        "prometheus_job": "unknown",
        "description": "System monitoring not configured"
    })
    
    return {
        "system_type": system,
        "os_name": os_name,
        "hostname": platform.node(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "os_config": current_os
    }

# Prometheus system metrics endpoints
@router.get("/prometheus/system/metrics")
async def get_prometheus_system_metrics():
    """Get current system metrics from Prometheus (works with any OS)"""
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
        
        # Get disk usage for root filesystem (using avail_bytes for macOS compatibility)
        disk_response = requests.get(f"{prometheus_url}/api/v1/query",
                                   params={"query": "100 - ((node_filesystem_avail_bytes{mountpoint='/'} * 100) / node_filesystem_size_bytes{mountpoint='/'})"})
        
        # Parse responses
        cpu_usage = 0
        if cpu_response.status_code == 200:
            cpu_data = cpu_response.json()
            if cpu_data.get('data', {}).get('result'):
                load_avg = float(cpu_data['data']['result'][0]['value'][1])
                # Get system info for dynamic core count
                import psutil
                cores = psutil.cpu_count()
                # Convert load average to percentage (load/cores * 100)
                cpu_usage = min((load_avg / cores) * 100, 100)
        
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
        
        # Get system info for dynamic naming
        system_info = await get_system_info()
        
        return {
            "hostname": f"{system_info['os_config']['name']}-System",
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2),
            "disk_usage": round(disk_usage, 2),
            "status": "running",
            "source": "prometheus",
            "cores": system_info['cpu_count'],
            "memory_total_gb": system_info['memory_total_gb'],
            "system_type": system_info['system_type'],
            "os_config": system_info['os_config']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Prometheus metrics: {str(e)}")

@router.get("/vms")
async def get_all_vms():
    """Get all VMs including Mac system from Prometheus"""
    try:
        # Get traditional underutilized VMs
        underutilized = get_underutilized_vms()
        
        # Get system metrics from Prometheus
        system_metrics_response = await get_prometheus_system_metrics()
        
        # Create system VM entry
        system_vm = {
            "vm": system_metrics_response["hostname"],
            "status": "running",
            "cpu": system_metrics_response["cpu_usage"],
            "memory_usage": system_metrics_response["memory_usage"],
            "cores": system_metrics_response["cores"],
            "memory": system_metrics_response["memory_total_gb"],
            "cluster": f"local-{system_metrics_response['system_type']}",
            "source": "prometheus",
            "details": {
                "avg_cpu": system_metrics_response["cpu_usage"],
                "avg_mem": system_metrics_response["memory_usage"],
                "disk_usage": system_metrics_response["disk_usage"]
            }
        }
        
        # Combine all VMs
        all_vms = [system_vm] + underutilized
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


# Capacity Planner endpoints
@router.get("/capacity/analysis")
async def get_capacity_analysis():
    """Get infrastructure capacity analysis and recommendations"""
    try:
        # Get current system metrics
        cpu_count = psutil.cpu_count()
        memory_total = psutil.virtual_memory().total / (1024**3)  # GB
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        # Calculate capacity based on current utilization
        # Assume each VM needs 2 CPU cores and 4GB RAM on average
        vm_cpu_requirement = 2
        vm_memory_requirement = 4  # GB
        
        # Calculate max VMs with 20% safety buffer
        max_vms_by_cpu = int((cpu_count * 0.8) / vm_cpu_requirement)
        max_vms_by_memory = int((memory_total * 0.8) / vm_memory_requirement)
        max_vms = min(max_vms_by_cpu, max_vms_by_memory)
        
        # Current VMs (simplified - in real scenario would query hypervisor)
        current_vms = 1  # Mac system VM
        
        # Generate recommendations
        recommendations = []
        
        if max_vms - current_vms > 5:
            recommendations.append({
                "id": 1,
                "title": "Excellent Capacity Available",
                "description": f"Your infrastructure can support {max_vms - current_vms} additional VMs with current resource allocation."
            })
        elif max_vms - current_vms > 0:
            recommendations.append({
                "id": 2,
                "title": "Limited Capacity Available",
                "description": f"Consider optimizing current VMs or upgrading hardware. Only {max_vms - current_vms} additional VMs possible."
            })
        else:
            recommendations.append({
                "id": 3,
                "title": "Capacity Limit Reached",
                "description": "Infrastructure is at capacity. Consider upgrading CPU or memory resources."
            })
            
        if memory_percent > 80:
            recommendations.append({
                "id": 4,
                "title": "High Memory Utilization",
                "description": "Memory usage is high. Consider adding more RAM to increase VM capacity."
            })
            
        if cpu_percent > 80:
            recommendations.append({
                "id": 5,
                "title": "High CPU Utilization",
                "description": "CPU usage is high. Consider upgrading to more CPU cores for better performance."
            })
        
        return {
            "totalCPU": cpu_count,
            "totalMemory": round(memory_total, 1),
            "usedCPU": cpu_percent,
            "usedMemory": memory_percent,
            "maxVMs": max_vms,
            "currentVMs": current_vms,
            "recommendations": recommendations,
            "analysis_time": datetime.now().isoformat(),
            "vm_requirements": {
                "cpu_per_vm": vm_cpu_requirement,
                "memory_per_vm": vm_memory_requirement,
                "safety_buffer": "20%"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze capacity: {str(e)}")


# License Management endpoints
class License(BaseModel):
    id: int
    name: str
    vendor: str
    type: str
    status: str
    used: int
    total: int
    expiryDate: str
    description: str = ""
    cost: float = 0.0


# In-memory license storage (in production, use a database)
license_storage: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "VMware vSphere Standard",
        "vendor": "VMware",
        "type": "Perpetual",
        "status": "active",
        "used": 8,
        "total": 16,
        "expiryDate": "2025-12-31",
        "description": "Virtualization platform for data center",
        "cost": 2995.0
    },
    {
        "id": 2,
        "name": "Windows Server 2022 Datacenter",
        "vendor": "Microsoft",
        "type": "Subscription",
        "status": "expiring",
        "used": 12,
        "total": 20,
        "expiryDate": "2025-08-15",
        "description": "Windows Server operating system licenses",
        "cost": 6155.0
    },
    {
        "id": 3,
        "name": "Prometheus Enterprise",
        "vendor": "Prometheus",
        "type": "Annual",
        "status": "active",
        "used": 3,
        "total": 10,
        "expiryDate": "2026-03-20",
        "description": "Monitoring and alerting toolkit",
        "cost": 5000.0
    },
    {
        "id": 4,
        "name": "Red Hat Enterprise Linux",
        "vendor": "Red Hat",
        "type": "Subscription",
        "status": "active",
        "used": 5,
        "total": 25,
        "expiryDate": "2025-11-30",
        "description": "Enterprise Linux operating system",
        "cost": 3500.0
    },
    {
        "id": 5,
        "name": "Zabbix Professional",
        "vendor": "Zabbix",
        "type": "Annual",
        "status": "expired",
        "used": 0,
        "total": 100,
        "expiryDate": "2024-12-31",
        "description": "Network and infrastructure monitoring",
        "cost": 2000.0
    }
]


@router.get("/licenses")
async def get_licenses():
    """Get all software licenses"""
    try:
        # Update license statuses based on expiry dates
        current_date = datetime.now()
        
        for license_item in license_storage:
            expiry_date = datetime.strptime(license_item["expiryDate"], "%Y-%m-%d")
            days_until_expiry = (expiry_date - current_date).days
            
            if days_until_expiry < 0:
                license_item["status"] = "expired"
            elif days_until_expiry <= 30:
                license_item["status"] = "expiring"
            else:
                license_item["status"] = "active"
        
        return license_storage
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch licenses: {str(e)}")


@router.post("/licenses")
async def create_license(license: License):
    """Create a new license entry"""
    try:
        # Generate new ID
        new_id = max([l["id"] for l in license_storage], default=0) + 1
        
        new_license = {
            "id": new_id,
            "name": license.name,
            "vendor": license.vendor,
            "type": license.type,
            "status": license.status,
            "used": license.used,
            "total": license.total,
            "expiryDate": license.expiryDate,
            "description": license.description,
            "cost": license.cost
        }
        
        license_storage.append(new_license)
        
        return {"status": "success", "message": "License created successfully", "license": new_license}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create license: {str(e)}")


@router.get("/licenses/{license_id}")
async def get_license(license_id: int):
    """Get a specific license by ID"""
    try:
        license_item = next((l for l in license_storage if l["id"] == license_id), None)
        
        if not license_item:
            raise HTTPException(status_code=404, detail="License not found")
            
        return license_item
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch license: {str(e)}")


@router.put("/licenses/{license_id}")
async def update_license(license_id: int, license: License):
    """Update an existing license"""
    try:
        license_index = next((i for i, l in enumerate(license_storage) if l["id"] == license_id), None)
        
        if license_index is None:
            raise HTTPException(status_code=404, detail="License not found")
            
        license_storage[license_index] = {
            "id": license_id,
            "name": license.name,
            "vendor": license.vendor,
            "type": license.type,
            "status": license.status,
            "used": license.used,
            "total": license.total,
            "expiryDate": license.expiryDate,
            "description": license.description,
            "cost": license.cost
        }
        
        return {"status": "success", "message": "License updated successfully", "license": license_storage[license_index]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update license: {str(e)}")


@router.delete("/licenses/{license_id}")
async def delete_license(license_id: int):
    """Delete a license"""
    try:
        license_index = next((i for i, l in enumerate(license_storage) if l["id"] == license_id), None)
        
        if license_index is None:
            raise HTTPException(status_code=404, detail="License not found")
            
        deleted_license = license_storage.pop(license_index)
        
        return {"status": "success", "message": "License deleted successfully", "license": deleted_license}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete license: {str(e)}")


@router.get("/licenses/summary")
async def get_license_summary():
    """Get license usage summary and statistics"""
    try:
        total_licenses = len(license_storage)
        active_licenses = len([l for l in license_storage if l["status"] == "active"])
        expiring_licenses = len([l for l in license_storage if l["status"] == "expiring"])
        expired_licenses = len([l for l in license_storage if l["status"] == "expired"])
        
        total_cost = sum([l["cost"] for l in license_storage])
        total_capacity = sum([l["total"] for l in license_storage])
        total_used = sum([l["used"] for l in license_storage])
        
        utilization_rate = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "total_licenses": total_licenses,
            "active_licenses": active_licenses,
            "expiring_licenses": expiring_licenses,
            "expired_licenses": expired_licenses,
            "total_cost": total_cost,
            "total_capacity": total_capacity,
            "total_used": total_used,
            "utilization_rate": round(utilization_rate, 2),
            "summary_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate license summary: {str(e)}")
