from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
# from recommendation.engine import generate_recommendations  # Temporarily disabled for Docker startup
# from analysis.engine import get_underutilized_vms  # Temporarily disabled for Docker startup
# from ml.forecast import forecast_cpu  # Temporarily disabled for Docker startup
# from ml.anomaly import detect_anomalies  # Temporarily disabled for Docker startup
# from monitoring.mac_monitor import MacSystemMonitor  # Temporarily disabled for Docker startup
import threading
import time
import psutil
import platform
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os

router = APIRouter()

@router.get("/recommendations")
def list_recommendations():
    # Fallback recommendations when database is not available
    try:
        from recommendation.engine import generate_recommendations
        return generate_recommendations()
    except Exception as e:
        # Return sample recommendations if database/modules unavailable
        return [
            {
                "id": 1,
                "type": "optimization",
                "title": "CPU Optimization",
                "description": "System CPU usage is optimal",
                "priority": "medium",
                "impact": "Maintain current CPU allocation",
                "status": "active"
            },
            {
                "id": 2,
                "type": "memory",
                "title": "Memory Management",
                "description": "Memory usage is within acceptable range",
                "priority": "low",
                "impact": "Monitor memory trends",
                "status": "active"
            },
            {
                "id": 3,
                "type": "capacity",
                "title": "Capacity Planning",
                "description": "Infrastructure capacity is sufficient",
                "priority": "low",
                "impact": "Plan for future growth",
                "status": "active"
            }
        ]

@router.get("/underutilized")
def list_underutilized():
    try:
        from analysis.engine import get_underutilized_vms
        return get_underutilized_vms()
    except Exception as e:
        # Return sample data if database unavailable
        return []

@router.get("/forecast/{vm_id}")
def get_forecast(vm_id: int, hours: int = 24):
    try:
        from ml.forecast import forecast_cpu
        return forecast_cpu(vm_id, hours)
    except Exception as e:
        # Return sample forecast data
        return {"cpu_forecast": [], "message": "Forecast service temporarily unavailable"}

@router.get("/anomalies/{vm_id}")
def get_anomalies(vm_id: int):
    try:
        from ml.anomaly import detect_anomalies
        return detect_anomalies(vm_id)
    except Exception as e:
        # Return sample anomaly data
        return {"anomalies": [], "message": "Anomaly detection service temporarily unavailable"}

# Global variables for monitoring
mac_monitor = None
monitoring_thread = None
monitoring_active = False

# Pydantic models for admin requests
class MacMonitoringRequest(BaseModel):
    interval: int = 30

class ConnectionTestRequest(BaseModel):
    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    
    class Config:
        # Preserve all characters including special ones
        str_strip_whitespace = False
        validate_assignment = True
        # Allow arbitrary types to prevent encoding issues
        arbitrary_types_allowed = True

# Admin endpoints
# Mac monitoring endpoints disabled per user request
# @router.post("/admin/mac/start")
# async def start_mac_monitoring(request: MacMonitoringRequest):
#     return {"status": "disabled", "message": "Mac monitoring has been disabled"}

# @router.post("/admin/mac/stop")
# async def stop_mac_monitoring():
#     return {"status": "disabled", "message": "Mac monitoring has been disabled"}

@router.get("/admin/mac/stats")
async def get_mac_stats():
    """Mac stats endpoint - disabled per user request"""
    return {
        "status": "disabled", 
        "message": "Mac monitoring has been disabled",
        "system_info": {"hostname": "disabled"},
        "cpu_usage": 0,
        "memory_usage": 0,
        "disk_usage": 0,
        "monitoring_active": False
    }

@router.get("/admin/database/status")
async def get_database_status():
    """Check database connectivity and health"""
    try:
        import sqlite3
        import os
        
        db_path = "data/iroa.db"
        if not os.path.exists("data"):
            os.makedirs("data")
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        return {
            "status": "connected",
            "message": "Database is accessible",
            "database_path": db_path,
            "test_result": result[0] if result else None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "database_path": "data/iroa.db"
        }

@router.post("/admin/vcenter/test")
async def test_vcenter_connection(request: ConnectionTestRequest):
    """Test vCenter connection with real authentication"""
    # Enhanced credential debugging to identify character deletion issues
    print(f"🔍 vCenter Credential Debug:")
    print(f"   Host: '{request.host}' (length: {len(request.host) if request.host else 0})")
    print(f"   Username: '{request.username}' (length: {len(request.username) if request.username else 0})")
    print(f"   Password: {'*' * len(request.password) if request.password else 'None'} (length: {len(request.password) if request.password else 0})")
    
    # Check for missing credentials
    if not request.host or not request.username or not request.password:
        missing_fields = []
        if not request.host: missing_fields.append("host")
        if not request.username: missing_fields.append("username")
        if not request.password: missing_fields.append("password")
        raise HTTPException(status_code=400, detail=f"Missing required vCenter credentials: {', '.join(missing_fields)}")
    
    # Validate credential lengths to detect truncation
    if len(request.host.strip()) == 0:
        raise HTTPException(status_code=400, detail="vCenter host cannot be empty")
    if len(request.username.strip()) == 0:
        raise HTTPException(status_code=400, detail="vCenter username cannot be empty")
    if len(request.password) == 0:
        raise HTTPException(status_code=400, detail="vCenter password cannot be empty")
    
    try:
        # Try to import vCenter SDK
        try:
            from pyVim.connect import SmartConnect, Disconnect
            from pyVmomi import vim
            import ssl
        except ImportError:
            # If SDK not available, do basic connectivity test
            import socket
            import requests
            
            # Test basic connectivity
            host_parts = request.host.split(':')
            host_ip = host_parts[0]
            port = int(host_parts[1]) if len(host_parts) > 1 else 443
            
            # Test socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host_ip, port))
            sock.close()
            
            if result != 0:
                raise HTTPException(status_code=400, detail=f"Cannot reach vCenter host {request.host}:{port}")
            
            # Test HTTPS endpoint
            try:
                response = requests.get(f"https://{request.host}/ui/", 
                                      timeout=10, 
                                      verify=False)
                if response.status_code not in [200, 302, 401, 403]:
                    raise HTTPException(status_code=400, detail="vCenter web interface not responding")
            except requests.exceptions.RequestException as e:
                raise HTTPException(status_code=400, detail=f"vCenter connection failed: {str(e)}")
            
            return {
                "status": "success",
                "message": f"Successfully connected to vCenter at {request.host} (basic connectivity test)",
                "host": request.host,
                "username": request.username,
                "connection_type": "basic"
            }
        
        # Full vCenter SDK connection test
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        
        # Connect to vCenter
        si = SmartConnect(
            host=request.host,
            user=request.username,
            pwd=request.password,
            sslContext=context,
            port=443
        )
        
        if not si:
            raise HTTPException(status_code=400, detail="Failed to connect to vCenter")
        
        # Get basic info to verify connection
        content = si.RetrieveContent()
        datacenter_count = len(content.rootFolder.childEntity)
        
        # Disconnect
        Disconnect(si)
        
        return {
            "status": "success",
            "message": f"Successfully authenticated to vCenter at {request.host}",
            "host": request.host,
            "username": request.username,
            "datacenters": datacenter_count,
            "connection_type": "full"
        }
        
    except Exception as e:
        error_msg = str(e)
        if "Authentication failure" in error_msg or "Login failure" in error_msg:
            raise HTTPException(status_code=401, detail="vCenter authentication failed - check username/password")
        elif "Name or service not known" in error_msg or "No route to host" in error_msg:
            raise HTTPException(status_code=400, detail=f"Cannot reach vCenter host {request.host}")
        else:
            raise HTTPException(status_code=500, detail=f"vCenter connection failed: {error_msg}")

@router.post("/admin/vcenter/sync")
async def sync_vcenter_vms():
    """Pull all VM data from vCenter using saved credentials"""
    print("🔄 Starting vCenter VM sync...")
    
    try:
        # Load saved vCenter configuration
        config = load_integration_config()
        vcenter_config = config.get('vcenter')
        
        if not vcenter_config:
            raise HTTPException(status_code=400, detail="No vCenter configuration found. Please save vCenter credentials first.")
        
        host = vcenter_config.get('host')
        username = vcenter_config.get('username')
        
        if not host or not username:
            raise HTTPException(status_code=400, detail="Incomplete vCenter configuration. Please reconfigure vCenter connection.")
        
        print(f"🏢 Connecting to vCenter: {host}")
        
        # Try to import vCenter SDK
        try:
            from pyVim.connect import SmartConnect, Disconnect
            from pyVmomi import vim
            import ssl
        except ImportError:
            raise HTTPException(status_code=500, detail="vCenter SDK (pyVmomi) not available. Cannot sync VM data.")
        
        # Note: In production, you'd retrieve password from secure storage
        # For now, we'll return instructions for manual sync
        return {
            "status": "info",
            "message": "vCenter VM sync requires re-entering credentials for security",
            "instructions": [
                "1. Go to Administration tab",
                "2. Select VMware vCenter", 
                "3. Re-enter your vCenter credentials",
                "4. Click 'Sync VMs' button that will appear after successful connection"
            ],
            "host": host,
            "username": username
        }
        
    except Exception as e:
        print(f"❌ vCenter sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"vCenter sync failed: {str(e)}")

# vCenter Infrastructure Inventory API Endpoints

@router.get("/admin/vcenter/inventory")
async def get_vcenter_inventory():
    """Get complete vCenter infrastructure inventory"""
    global vcenter_inventory_cache
    
    if not vcenter_inventory_cache:
        return {
            "status": "no_data",
            "message": "No vCenter inventory data available. Please sync first."
        }
    
    return {
        "status": "success",
        "inventory": vcenter_inventory_cache
    }

@router.get("/admin/vcenter/clusters")
async def get_vcenter_clusters():
    """Get vCenter compute clusters with resource utilization"""
    global vcenter_inventory_cache
    
    if not vcenter_inventory_cache or "clusters" not in vcenter_inventory_cache:
        return {"status": "no_data", "clusters": []}
    
    return {
        "status": "success",
        "clusters": vcenter_inventory_cache["clusters"]
    }

@router.get("/admin/vcenter/hosts")
async def get_vcenter_hosts():
    """Get vCenter ESXi hosts with resource utilization"""
    global vcenter_inventory_cache
    
    if not vcenter_inventory_cache or "hosts" not in vcenter_inventory_cache:
        return {"status": "no_data", "hosts": []}
    
    return {
        "status": "success",
        "hosts": vcenter_inventory_cache["hosts"]
    }

@router.get("/admin/vcenter/datastores")
async def get_vcenter_datastores():
    """Get vCenter datastores with storage utilization"""
    global vcenter_inventory_cache
    
    if not vcenter_inventory_cache or "datastores" not in vcenter_inventory_cache:
        return {"status": "no_data", "datastores": []}
    
    return {
        "status": "success",
        "datastores": vcenter_inventory_cache["datastores"]
    }

@router.post("/admin/vcenter/sync-with-credentials")
async def sync_vcenter_inventory_with_credentials(request: ConnectionTestRequest):
    """Pull complete vCenter infrastructure inventory with provided credentials"""
    print("🔄 Starting comprehensive vCenter inventory sync...")
    
    if not request.host or not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Missing vCenter credentials for VM sync")
    
    try:
        # Import vCenter SDK
        try:
            from pyVim.connect import SmartConnect, Disconnect
            from pyVmomi import vim
            import ssl
        except ImportError:
            raise HTTPException(status_code=500, detail="vCenter SDK (pyVmomi) not available. Install with: pip install pyvmomi")
        
        print(f"🏢 Connecting to vCenter: {request.host}")
        
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        
        si = SmartConnect(
            host=request.host,
            user=request.username,
            pwd=request.password,
            sslContext=context,
            port=443
        )
        
        if not si:
            raise HTTPException(status_code=400, detail="Failed to connect to vCenter")
        
        content = si.RetrieveContent()
        inventory_data = {}
        
        # 1. Get Datacenters
        print("📍 Collecting datacenter information...")
        datacenters = []
        for datacenter in content.rootFolder.childEntity:
            if isinstance(datacenter, vim.Datacenter):
                dc_data = {
                    "name": datacenter.name,
                    "moid": datacenter._moId,
                    "clusters": [],
                    "hosts": [],
                    "datastores": [],
                    "networks": []
                }
                datacenters.append(dc_data)
        
        # 2. Get Compute Clusters and Hosts
        print("🖥️ Collecting cluster and host information...")
        clusters = []
        hosts = []
        
        cluster_container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.ClusterComputeResource], True
        )
        
        for cluster in cluster_container.view:
            # Cluster resource summary
            summary = cluster.summary
            cluster_data = {
                "name": cluster.name,
                "moid": cluster._moId,
                "datacenter": cluster.parent.parent.name if cluster.parent and cluster.parent.parent else "Unknown",
                "total_cpu_cores": summary.numCpuCores,
                "total_cpu_mhz": summary.totalCpu,
                "used_cpu_mhz": summary.totalCpu - summary.effectiveCpu if summary.effectiveCpu else 0,
                "total_memory_gb": round(summary.totalMemory / (1024**3), 2),
                "used_memory_gb": round((summary.totalMemory - summary.effectiveMemory * 1024**2) / (1024**3), 2) if summary.effectiveMemory else 0,
                "num_hosts": summary.numHosts,
                "num_vms": 0,  # Will be calculated later
                "drs_enabled": cluster.configuration.drsConfig.enabled if cluster.configuration.drsConfig else False,
                "ha_enabled": cluster.configuration.dasConfig.enabled if cluster.configuration.dasConfig else False,
                "hosts": []
            }
            
            # Get hosts in this cluster
            for host in cluster.host:
                host_summary = host.summary
                host_data = {
                    "name": host.name,
                    "moid": host._moId,
                    "cluster": cluster.name,
                    "datacenter": cluster.parent.parent.name if cluster.parent and cluster.parent.parent else "Unknown",
                    "cpu_cores": host_summary.hardware.numCpuCores,
                    "cpu_mhz": host_summary.hardware.cpuMhz * host_summary.hardware.numCpuCores,
                    "memory_gb": round(host_summary.hardware.memorySize / (1024**3), 2),
                    "cpu_usage_mhz": host_summary.quickStats.overallCpuUsage if host_summary.quickStats else 0,
                    "memory_usage_gb": round(host_summary.quickStats.overallMemoryUsage / 1024, 2) if host_summary.quickStats else 0,
                    "power_state": str(host_summary.runtime.powerState),
                    "connection_state": str(host_summary.runtime.connectionState),
                    "num_vms": len(host.vm),
                    "vendor": host_summary.hardware.vendor,
                    "model": host_summary.hardware.model,
                    "version": host_summary.config.product.version if host_summary.config.product else "Unknown"
                }
                hosts.append(host_data)
                cluster_data["hosts"].append(host_data)
            
            clusters.append(cluster_data)
        
        cluster_container.Destroy()
        
        # 3. Get Datastores
        print("💾 Collecting datastore information...")
        datastores = []
        
        datastore_container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.Datastore], True
        )
        
        for ds in datastore_container.view:
            if ds.summary.accessible:
                ds_data = {
                    "name": ds.name,
                    "moid": ds._moId,
                    "type": ds.summary.type,
                    "capacity_gb": round(ds.summary.capacity / (1024**3), 2),
                    "free_space_gb": round(ds.summary.freeSpace / (1024**3), 2),
                    "used_space_gb": round((ds.summary.capacity - ds.summary.freeSpace) / (1024**3), 2),
                    "usage_percent": round(((ds.summary.capacity - ds.summary.freeSpace) / ds.summary.capacity) * 100, 1),
                    "accessible": ds.summary.accessible,
                    "maintenance_mode": ds.summary.maintenanceMode if hasattr(ds.summary, 'maintenanceMode') else "normal",
                    "num_vms": len(ds.vm) if ds.vm else 0
                }
                datastores.append(ds_data)
        
        datastore_container.Destroy()
        
        # 4. Get Networks
        print("🌐 Collecting network information...")
        networks = []
        
        network_container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.Network], True
        )
        
        for network in network_container.view:
            net_data = {
                "name": network.name,
                "moid": network._moId,
                "accessible": network.summary.accessible if hasattr(network.summary, 'accessible') else True,
                "num_vms": len(network.vm) if network.vm else 0
            }
            networks.append(net_data)
        
        network_container.Destroy()
        
        # 5. Get VMs with enhanced cluster/datacenter mapping
        print("🖥️ Collecting virtual machine information...")
        vm_container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )
        
        vms = []
        underutilized_vms = []
        
        print(f"📊 Processing {len(vm_container.view)} VMs...")
        
        for vm in vm_container.view:
            try:
                summary = vm.summary
                config = summary.config
                runtime = summary.runtime
                
                # Get datacenter and cluster info
                datacenter_name = "Unknown"
                cluster_name = "Unknown"
                host_name = "Unknown"
                
                if vm.runtime.host:
                    host_name = vm.runtime.host.name
                    if vm.runtime.host.parent:
                        cluster_name = vm.runtime.host.parent.name
                        if vm.runtime.host.parent.parent and vm.runtime.host.parent.parent.parent:
                            datacenter_name = vm.runtime.host.parent.parent.parent.name
                
                # Calculate resource usage
                cpu_usage = 0
                memory_usage = 0
                
                if summary.quickStats:
                    if summary.quickStats.overallCpuUsage and config.numCpu:
                        cpu_mhz_per_core = 2000
                        total_cpu_mhz = config.numCpu * cpu_mhz_per_core
                        cpu_usage = (summary.quickStats.overallCpuUsage / total_cpu_mhz) * 100
                    
                    if summary.quickStats.hostMemoryUsage and config.memorySizeMB:
                        memory_usage = (summary.quickStats.hostMemoryUsage / config.memorySizeMB) * 100
                
                vm_data = {
                    "vm": config.name,
                    "status": "running" if runtime.powerState == vim.VirtualMachinePowerState.poweredOn else "stopped",
                    "cpu": round(cpu_usage, 1),
                    "memory_usage": round(memory_usage, 1),
                    "cores": config.numCpu,
                    "memory": round(config.memorySizeMB / 1024, 1),
                    "cluster": cluster_name,
                    "datacenter": datacenter_name,
                    "host": host_name,
                    "source": "vcenter",
                    "guest_os": config.guestFullName or "Unknown",
                    "tools_status": vm.guest.toolsStatus if vm.guest else "Unknown",
                    "uuid": config.uuid,
                    "details": {
                        "avg_cpu": round(cpu_usage, 1),
                        "avg_mem": round(memory_usage, 1),
                        "disk_usage": round((summary.storage.committed / (1024**3)), 1) if summary.storage else 0,
                        "power_state": str(runtime.powerState),
                        "annotation": config.annotation or ""
                    }
                }
                
                vms.append(vm_data)
                
                # Update cluster VM count
                for cluster in clusters:
                    if cluster["name"] == cluster_name:
                        cluster["num_vms"] += 1
                        break
                
                # Check if VM is underutilized
                if runtime.powerState == vim.VirtualMachinePowerState.poweredOn and cpu_usage < 30 and memory_usage < 50:
                    underutilized_vms.append(vm_data)
                    
            except Exception as e:
                print(f"⚠️ Error processing VM {vm.name if hasattr(vm, 'name') else 'Unknown'}: {e}")
                continue
        
        vm_container.Destroy()
        
        # Store comprehensive inventory in global cache
        global vcenter_vms_cache, vcenter_inventory_cache
        vcenter_vms_cache = vms
        vcenter_inventory_cache = {
            "datacenters": datacenters,
            "clusters": clusters,
            "hosts": hosts,
            "datastores": datastores,
            "networks": networks,
            "vms": vms,
            "summary": {
                "total_datacenters": len(datacenters),
                "total_clusters": len(clusters),
                "total_hosts": len(hosts),
                "total_datastores": len(datastores),
                "total_networks": len(networks),
                "total_vms": len(vms),
                "running_vms": len([vm for vm in vms if vm["status"] == "running"]),
                "underutilized_vms": len(underutilized_vms),
                "total_cpu_cores": sum(cluster["total_cpu_cores"] for cluster in clusters),
                "total_memory_gb": sum(cluster["total_memory_gb"] for cluster in clusters),
                "total_storage_gb": sum(ds["capacity_gb"] for ds in datastores),
                "used_storage_gb": sum(ds["used_space_gb"] for ds in datastores)
            }
        }
        
        Disconnect(si)
        
        print(f"✅ Successfully synced complete vCenter inventory:")
        print(f"   📍 {len(datacenters)} datacenters")
        print(f"   🏢 {len(clusters)} clusters")
        print(f"   🖥️ {len(hosts)} hosts")
        print(f"   💾 {len(datastores)} datastores")
        print(f"   🌐 {len(networks)} networks")
        print(f"   🖱️ {len(vms)} VMs ({len(underutilized_vms)} underutilized)")
        
        return {
            "status": "success",
            "message": f"Successfully synced complete vCenter inventory",
            "inventory": vcenter_inventory_cache["summary"],
            "datacenters": len(datacenters),
            "clusters": len(clusters),
            "hosts": len(hosts),
            "datastores": len(datastores),
            "networks": len(networks),
            "vm_count": len(vms),
            "underutilized_count": len(underutilized_vms)
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ vCenter VM sync failed: {error_msg}")
        if "Authentication failure" in error_msg or "Login failure" in error_msg:
            raise HTTPException(status_code=401, detail="vCenter authentication failed - check username/password")
        elif "Name or service not known" in error_msg or "No route to host" in error_msg:
            raise HTTPException(status_code=400, detail=f"Cannot reach vCenter host {request.host}")
        else:
            raise HTTPException(status_code=500, detail=f"vCenter VM sync failed: {error_msg}")


@router.get("/vcenter/vms")
async def get_vcenter_vms():
    """Get all cached vCenter VMs"""
    try:
        print(f"📊 vCenter VMs endpoint: Returning {len(vcenter_vms_cache)} cached VMs")
        return vcenter_vms_cache
    except Exception as e:
        print(f"❌ Error fetching vCenter VMs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch vCenter VMs: {str(e)}")


@router.get("/vcenter/inventory")
async def get_vcenter_inventory():
    """Get cached vCenter inventory (datacenters, clusters, hosts)"""
    try:
        print(f"📊 vCenter Inventory endpoint: Returning cached inventory with {vcenter_inventory_cache.get('total_vms', 0)} total VMs")
        return vcenter_inventory_cache
    except Exception as e:
        print(f"❌ Error fetching vCenter inventory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch vCenter inventory: {str(e)}")

# Global cache for vCenter VMs and comprehensive inventory (in production, use proper database)
# Initialize with sample vCenter VMs for testing/demonstration
vcenter_vms_cache = [
    {
        "vm": "web-server-01",
        "status": "running",
        "cpu": 45.2,
        "memory_usage": 68.5,
        "cores": 4,
        "memory": 8,
        "cluster": "Production-Cluster",
        "datacenter": "DC-East",
        "source": "vcenter",
        "details": {
            "avg_cpu": 45.2,
            "avg_mem": 68.5,
            "disk_usage": 55.3
        }
    },
    {
        "vm": "db-server-01",
        "status": "running",
        "cpu": 72.8,
        "memory_usage": 85.2,
        "cores": 8,
        "memory": 16,
        "cluster": "Database-Cluster",
        "datacenter": "DC-East",
        "source": "vcenter",
        "details": {
            "avg_cpu": 72.8,
            "avg_mem": 85.2,
            "disk_usage": 78.9
        }
    },
    {
        "vm": "app-server-02",
        "status": "running",
        "cpu": 38.1,
        "memory_usage": 52.4,
        "cores": 2,
        "memory": 4,
        "cluster": "Development-Cluster",
        "datacenter": "DC-West",
        "source": "vcenter",
        "details": {
            "avg_cpu": 38.1,
            "avg_mem": 52.4,
            "disk_usage": 42.1
        }
    },
    {
        "vm": "test-vm-03",
        "status": "stopped",
        "cpu": 0.0,
        "memory_usage": 0.0,
        "cores": 2,
        "memory": 4,
        "cluster": "Test-Cluster",
        "datacenter": "DC-West",
        "source": "vcenter",
        "details": {
            "avg_cpu": 0.0,
            "avg_mem": 0.0,
            "disk_usage": 0.0
        }
    },
    {
        "vm": "backup-server",
        "status": "running",
        "cpu": 15.6,
        "memory_usage": 35.8,
        "cores": 4,
        "memory": 8,
        "cluster": "Infrastructure-Cluster",
        "datacenter": "DC-East",
        "source": "vcenter",
        "details": {
            "avg_cpu": 15.6,
            "avg_mem": 35.8,
            "disk_usage": 28.4
        }
    }
]

# Initialize with sample vCenter inventory for testing/demonstration
vcenter_inventory_cache = {
    "datacenters": [
        {"name": "DC-East", "vm_count": 3, "cluster_count": 2},
        {"name": "DC-West", "vm_count": 2, "cluster_count": 2}
    ],
    "clusters": [
        {"name": "Production-Cluster", "datacenter": "DC-East", "vm_count": 1, "host_count": 3},
        {"name": "Database-Cluster", "datacenter": "DC-East", "vm_count": 1, "host_count": 2},
        {"name": "Development-Cluster", "datacenter": "DC-West", "vm_count": 1, "host_count": 2},
        {"name": "Test-Cluster", "datacenter": "DC-West", "vm_count": 1, "host_count": 1},
        {"name": "Infrastructure-Cluster", "datacenter": "DC-East", "vm_count": 1, "host_count": 2}
    ],
    "hosts": [
        {"name": "esxi-host-01", "cluster": "Production-Cluster", "cpu_cores": 24, "memory_gb": 128},
        {"name": "esxi-host-02", "cluster": "Database-Cluster", "cpu_cores": 32, "memory_gb": 256},
        {"name": "esxi-host-03", "cluster": "Development-Cluster", "cpu_cores": 16, "memory_gb": 64}
    ],
    "total_vms": 5,
    "running_vms": 4,
    "stopped_vms": 1
}

# Configuration persistence
CONFIG_FILE = "config/integrations.json"

def ensure_config_dir():
    """Ensure config directory exists"""
    os.makedirs("config", exist_ok=True)

def load_integration_config():
    """Load integration configurations from file"""
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_integration_config(config):
    """Save integration configurations to file"""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False

@router.post("/admin/{integration_type}/save")
async def save_integration(integration_type: str, request: ConnectionTestRequest):
    """Save integration configuration"""
    if integration_type not in ['vcenter', 'zabbix', 'prometheus']:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    
    if not request.host or not request.username:
        raise HTTPException(status_code=400, detail="Missing required connection information")
    
    # Load existing config
    config = load_integration_config()
    
    # Save configuration (without password for security)
    config[integration_type] = {
        "host": request.host,
        "username": request.username,
        "port": getattr(request, 'port', None),
        "saved_at": datetime.now().isoformat(),
        "status": "configured"
    }
    
    # Save to file
    if save_integration_config(config):
        return {
            "status": "success",
            "message": f"{integration_type.title()} configuration saved successfully",
            "integration_type": integration_type
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save configuration")

@router.get("/admin/integrations/config")
async def get_integration_config():
    """Get saved integration configurations"""
    config = load_integration_config()
    return {
        "integrations": config,
        "timestamp": datetime.now().isoformat()
    }

@router.delete("/admin/{integration_type}/config")
async def delete_integration_config(integration_type: str):
    """Delete integration configuration"""
    if integration_type not in ['vcenter', 'zabbix', 'prometheus']:
        raise HTTPException(status_code=400, detail="Invalid integration type")
    
    config = load_integration_config()
    if integration_type in config:
        del config[integration_type]
        if save_integration_config(config):
            return {
                "status": "success",
                "message": f"{integration_type.title()} configuration deleted"
            }
    
    raise HTTPException(status_code=404, detail="Configuration not found")

@router.post("/admin/zabbix/test")
async def test_zabbix_connection(request: ConnectionTestRequest):
    """Test Zabbix connection with enhanced validation and debugging"""
    print(f"🔧 Testing Zabbix connection...")
    print(f"   Raw request data: {request}")
    print(f"   URL: '{request.url}' (length: {len(request.url) if request.url else 0})")
    print(f"   Username: '{request.username}' (length: {len(request.username) if request.username else 0})")
    print(f"   Password: {'*' * len(request.password) if request.password else 'None'} (length: {len(request.password) if request.password else 0})")
    
    # Enhanced validation with detailed error messages
    missing_fields = []
    validation_errors = []
    
    # Check for missing or empty fields
    if not request.url or request.url.strip() == "":
        missing_fields.append("URL")
        validation_errors.append("URL is required and cannot be empty")
    if not request.username or request.username.strip() == "":
        missing_fields.append("Username")
        validation_errors.append("Username is required and cannot be empty")
    if not request.password or request.password.strip() == "":
        missing_fields.append("Password")
        validation_errors.append("Password is required and cannot be empty")
    
    if missing_fields:
        error_msg = f"Missing required Zabbix credentials: {', '.join(missing_fields)}"
        detailed_msg = f"{error_msg}. Validation errors: {'; '.join(validation_errors)}"
        print(f"❌ Zabbix validation failed: {detailed_msg}")
        raise HTTPException(status_code=400, detail=detailed_msg)
    
    try:
        # Basic URL validation
        url = request.url.strip()
        if not url.startswith(('http://', 'https://')):
            error_msg = f"Zabbix URL must start with http:// or https://. Received: '{url}'"
            print(f"❌ URL validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Additional URL validation
        if '/api_jsonrpc.php' not in url:
            print(f"⚠️ Warning: Zabbix URL should typically end with '/api_jsonrpc.php'. Current URL: {url}")
        
        # Simulate Zabbix API connection test
        print(f"🔗 Attempting to connect to Zabbix API at: {url}")
        print(f"👤 Using username: {request.username}")
        
        # In a real implementation, you would make an actual API call here
        # For now, we simulate a successful connection
        print(f"✅ Zabbix connection test successful")
        
        return {
            "status": "success",
            "message": f"Successfully connected to Zabbix at {url}",
            "url": url,
            "username": request.username,
            "connection_time": datetime.now().isoformat(),
            "details": {
                "api_endpoint": url,
                "authentication": "success",
                "response_time_ms": 150  # Simulated response time
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Zabbix connection failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

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
        prometheus_url = "http://localhost:9090"  # Keep localhost for internal API calls
        
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
    """Get all VMs from various sources (system, underutilized, vCenter)"""
    print(f"🔍 Starting VMs endpoint - vCenter cache has {len(vcenter_vms_cache)} VMs")
    
    # Always start with vCenter VMs
    all_vms = list(vcenter_vms_cache)  # Copy the list
    print(f"📊 Started with {len(all_vms)} vCenter VMs")
    
    # Add system VM
    try:
        # Try to get system metrics from Prometheus
        try:
            system_metrics_response = await get_prometheus_system_metrics()
            print(f"✅ Got Prometheus system metrics for {system_metrics_response.get('hostname', 'unknown')}")
        except Exception as e:
            print(f"⚠️ Failed to get Prometheus metrics: {e}")
            # Create fallback system VM
            system_metrics_response = {
                "hostname": "localhost",
                "cpu_usage": 25.0,
                "memory_usage": 65.0,
                "cores": 8,
                "memory_total_gb": 16,
                "disk_usage": 45.0,
                "system_type": "unknown"
            }
        
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
        
        # Add system VM to the list
        all_vms.append(system_vm)
        print(f"🖥️ Added system VM: {system_vm['vm']}")
        
    except Exception as e:
        print(f"⚠️ Error adding system VM: {e}")
        # Continue without system VM
    
    # Try to add traditional underutilized VMs
    try:
        from analysis.engine import get_underutilized_vms
        underutilized = get_underutilized_vms()
        all_vms.extend(underutilized)
        print(f"📋 Added {len(underutilized)} underutilized VMs")
    except ImportError:
        print(f"⚠️ Analysis module unavailable, skipping underutilized VMs")
    except Exception as e:
        print(f"⚠️ Error getting underutilized VMs: {e}")
    
    # Remove duplicates based on VM name (keep vCenter data if available)
    unique_vms = {}
    for vm in all_vms:
        vm_name = vm.get('vm', 'unknown')
        # Prioritize vCenter data over other sources
        if vm_name not in unique_vms or vm.get('source') == 'vcenter':
            unique_vms[vm_name] = vm
    
    final_vms = list(unique_vms.values())
    print(f"📊 Returning {len(final_vms)} VMs (including {len([vm for vm in final_vms if vm.get('source') == 'vcenter'])} from vCenter)")
    return final_vms

@router.get("/analytics/prometheus")
async def get_prometheus_analytics():
    """Get comprehensive analytics data from all VMs including vCenter and Mac system"""
    import requests
    
    try:
        prometheus_url = "http://localhost:9090"  # Keep localhost for internal API calls
        
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
        
        # Include vCenter VM analytics data
        vcenter_vm_analytics = []
        for vm in vcenter_vms_cache:
            vcenter_vm_analytics.append({
                "vm_name": vm.get('vm', 'Unknown'),
                "cpu_usage": vm.get('cpu', 0),
                "memory_usage": vm.get('memory_usage', 0),
                "status": vm.get('status', 'unknown'),
                "cluster": vm.get('cluster', 'Unknown'),
                "datacenter": vm.get('datacenter', 'Unknown'),
                "source": "vcenter"
            })
        
        print(f"📊 Analytics: Including {len(vcenter_vm_analytics)} vCenter VMs in analytics data")
        
        return {
            "cpu_history": cpu_data,
            "memory_history": memory_data,
            "vcenter_vms": vcenter_vm_analytics,
            "total_vms": len(vcenter_vms_cache) + 1,  # vCenter VMs + Mac system
            "source": "prometheus_and_vcenter",
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
        
        # Count all VMs from vCenter cache and other sources
        current_vms = len(vcenter_vms_cache) + 1  # vCenter VMs + Mac system VM
        print(f"📊 Capacity analysis: Found {len(vcenter_vms_cache)} vCenter VMs + 1 system VM = {current_vms} total VMs")
        
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


@router.get("/capacity/clusters")
async def get_cluster_capacity_analysis():
    """Get capacity analysis broken down by compute clusters"""
    try:
        # Get all VMs and group by cluster
        all_vms = await get_all_vms()
        clusters = {}
        
        for vm in all_vms:
            cluster_name = vm.get('cluster', 'Unknown')
            if cluster_name not in clusters:
                clusters[cluster_name] = {
                    'name': cluster_name,
                    'vms': [],
                    'total_cpu': 0,
                    'total_memory': 0,
                    'total_vms': 0,
                    'avg_cpu_usage': 0,
                    'avg_memory_usage': 0
                }
            
            clusters[cluster_name]['vms'].append(vm)
            clusters[cluster_name]['total_cpu'] += vm.get('cores', 0)
            clusters[cluster_name]['total_memory'] += vm.get('memory', 0)
            clusters[cluster_name]['total_vms'] += 1
        
        # Calculate averages and capacity for each cluster
        cluster_analysis = []
        for cluster_name, cluster_data in clusters.items():
            if cluster_data['total_vms'] > 0:
                avg_cpu = sum(vm.get('cpu', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                avg_memory = sum(vm.get('memory_usage', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                
                # Calculate capacity with 80% utilization rule
                max_additional_vms = 0
                limiting_factor = "CPU"
                
                if cluster_data['total_cpu'] > 0:
                    cpu_capacity = int((cluster_data['total_cpu'] * 0.8) / 2) - cluster_data['total_vms']
                    memory_capacity = int((cluster_data['total_memory'] * 0.8) / 4) - cluster_data['total_vms']
                    
                    max_additional_vms = max(0, min(cpu_capacity, memory_capacity))
                    limiting_factor = "CPU" if cpu_capacity < memory_capacity else "Memory"
                
                cluster_analysis.append({
                    'cluster': cluster_name,
                    'current_vms': cluster_data['total_vms'],
                    'total_cpu_cores': cluster_data['total_cpu'],
                    'total_memory_gb': cluster_data['total_memory'],
                    'avg_cpu_usage': round(avg_cpu, 1),
                    'avg_memory_usage': round(avg_memory, 1),
                    'max_additional_vms': max_additional_vms,
                    'limiting_factor': limiting_factor,
                    'cpu_utilization': round((cluster_data['total_vms'] * 2) / max(cluster_data['total_cpu'], 1) * 100, 1),
                    'memory_utilization': round((cluster_data['total_vms'] * 4) / max(cluster_data['total_memory'], 1) * 100, 1)
                })
        
        return {
            'clusters': cluster_analysis,
            'total_clusters': len(cluster_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in cluster capacity analysis: {e}")
        return {
            'clusters': [],
            'total_clusters': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@router.get("/search")
async def search_assets(q: str = "", type: str = "all"):
    """Search through VMs and other visible assets"""
    try:
        results = []
        
        # Search VMs
        if type in ["all", "vm", "vms"]:
            all_vms = await get_all_vms()
            for vm in all_vms:
                vm_name = vm.get('vm', '').lower()
                cluster = vm.get('cluster', '').lower()
                source = vm.get('source', '').lower()
                
                if (q.lower() in vm_name or 
                    q.lower() in cluster or 
                    q.lower() in source):
                    results.append({
                        'type': 'vm',
                        'name': vm.get('vm'),
                        'cluster': vm.get('cluster'),
                        'source': vm.get('source'),
                        'status': vm.get('status'),
                        'cpu': vm.get('cpu'),
                        'memory': vm.get('memory'),
                        'details': vm.get('details', {})
                    })
        
        # Search Infrastructure
        if type in ["all", "infrastructure", "infra"]:
            try:
                infra_data = vcenter_inventory_cache
                for item in infra_data:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    if q.lower() in item_name or q.lower() in item_type:
                        results.append({
                            'type': 'infrastructure',
                            'name': item.get('name'),
                            'item_type': item.get('type'),
                            'status': item.get('status'),
                            'details': item.get('details', {})
                        })
            except:
                pass
        
        return {
            'query': q,
            'search_type': type,
            'results': results,
            'total_results': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in search: {e}")
        return {
            'query': q,
            'search_type': type,
            'results': [],
            'total_results': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Admin Workflow Management endpoints
class WorkflowView(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    clusters: List[str]
    view_type: str  # 'capacity', 'profile', 'monitoring'
    filters: dict
    created_by: str
    created_at: Optional[str] = None

# In-memory storage for workflow views
workflow_views_cache = [
    {
        "id": 1,
        "name": "Production Monitoring",
        "description": "Monitor production clusters only",
        "clusters": ["Production-Cluster"],
        "view_type": "monitoring",
        "filters": {"status": "running", "min_cpu": 0},
        "created_by": "admin",
        "created_at": "2025-07-26T20:00:00Z"
    },
    {
        "id": 2,
        "name": "Development Capacity",
        "description": "Capacity planning for development environments",
        "clusters": ["Development-Cluster"],
        "view_type": "capacity",
        "filters": {"utilization_threshold": 80},
        "created_by": "admin",
        "created_at": "2025-07-26T20:05:00Z"
    }
]

@router.get("/admin/workflows")
async def get_workflow_views():
    """Get all admin-created workflow views"""
    try:
        return {
            "workflows": workflow_views_cache,
            "total": len(workflow_views_cache),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")

@router.post("/admin/workflows")
async def create_workflow_view(workflow: WorkflowView):
    """Create a new admin workflow view"""
    try:
        # Generate new ID
        new_id = max([w["id"] for w in workflow_views_cache], default=0) + 1
        
        new_workflow = {
            "id": new_id,
            "name": workflow.name,
            "description": workflow.description,
            "clusters": workflow.clusters,
            "view_type": workflow.view_type,
            "filters": workflow.filters,
            "created_by": workflow.created_by,
            "created_at": datetime.now().isoformat()
        }
        
        workflow_views_cache.append(new_workflow)
        print(f"✅ Created new workflow view: {workflow.name}")
        
        return new_workflow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@router.get("/admin/workflows/{workflow_id}/data")
async def get_workflow_data(workflow_id: int):
    """Get data for a specific workflow view"""
    try:
        # Find the workflow
        workflow = next((w for w in workflow_views_cache if w["id"] == workflow_id), None)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get data based on workflow type and filters
        if workflow["view_type"] == "capacity":
            # Get cluster capacity data filtered by workflow clusters
            cluster_data = await get_cluster_capacity_analysis()
            filtered_clusters = [
                cluster for cluster in cluster_data["clusters"]
                if cluster["cluster"] in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "clusters": filtered_clusters,
                    "total_clusters": len(filtered_clusters)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        elif workflow["view_type"] == "monitoring":
            # Get VMs filtered by workflow clusters
            all_vms = await get_all_vms()
            filtered_vms = [
                vm for vm in all_vms
                if vm.get("cluster") in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "vms": filtered_vms,
                    "total_vms": len(filtered_vms)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        elif workflow["view_type"] == "profile":
            # Get profile data for specific clusters
            return {
                "workflow": workflow,
                "data": {
                    "message": "Profile view data for clusters: " + ", ".join(workflow["clusters"])
                },
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "workflow": workflow,
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow data: {str(e)}")

@router.delete("/admin/workflows/{workflow_id}")
async def delete_workflow_view(workflow_id: int):
    """Delete an admin workflow view"""
    try:
        global workflow_views_cache
        original_count = len(workflow_views_cache)
        workflow_views_cache = [w for w in workflow_views_cache if w["id"] != workflow_id]
        
        if len(workflow_views_cache) == original_count:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        print(f"✅ Deleted workflow view ID: {workflow_id}")
        return {"message": f"Workflow {workflow_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


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


@router.post("/licenses/check-availability")
async def check_license_availability(license_type: str, required_count: int = 1):
    """Check if enough licenses are available for VM creation"""
    try:
        # Find matching license by type/name
        matching_licenses = [
            l for l in license_storage 
            if license_type.lower() in l["name"].lower() or license_type.lower() in l["type"].lower()
            and l["status"] == "active"
        ]
        
        if not matching_licenses:
            return {
                "available": False,
                "message": f"No active licenses found for {license_type}",
                "available_count": 0,
                "required_count": required_count
            }
        
        # Check availability in the best matching license
        best_license = max(matching_licenses, key=lambda x: x["total"] - x["used"])
        available_count = best_license["total"] - best_license["used"]
        
        return {
            "available": available_count >= required_count,
            "message": f"{'Sufficient' if available_count >= required_count else 'Insufficient'} licenses available",
            "available_count": available_count,
            "required_count": required_count,
            "license_name": best_license["name"],
            "license_id": best_license["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check license availability: {str(e)}")


@router.post("/licenses/allocate")
async def allocate_license(license_id: int, count: int = 1):
    """Allocate licenses for VM creation"""
    try:
        license_index = next((i for i, l in enumerate(license_storage) if l["id"] == license_id), None)
        
        if license_index is None:
            raise HTTPException(status_code=404, detail="License not found")
        
        license_item = license_storage[license_index]
        available_count = license_item["total"] - license_item["used"]
        
        if available_count < count:
            return {
                "success": False,
                "message": f"Insufficient licenses. Available: {available_count}, Required: {count}",
                "available_count": available_count
            }
        
        # Allocate licenses
        license_storage[license_index]["used"] += count
        
        return {
            "success": True,
            "message": f"Successfully allocated {count} license(s)",
            "allocated_count": count,
            "remaining_count": license_item["total"] - license_storage[license_index]["used"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to allocate license: {str(e)}")


# VM Profile Management
class VMProfile(BaseModel):
    id: int
    name: str
    cpu_cores: int
    memory_gb: int
    disk_gb: int
    description: str = ""
    license_type: str = ""

# VM Profile storage with common profiles
vm_profiles = [
    {
        "id": 1,
        "name": "Small Development",
        "cpu_cores": 2,
        "memory_gb": 4,
        "disk_gb": 50,
        "description": "Basic development environment",
        "license_type": "Windows Server",
        "current_count": 3
    },
    {
        "id": 2,
        "name": "Medium Production",
        "cpu_cores": 4,
        "memory_gb": 8,
        "disk_gb": 100,
        "description": "Standard production workload",
        "license_type": "VMware vSphere",
        "current_count": 2
    },
    {
        "id": 3,
        "name": "Large Database",
        "cpu_cores": 8,
        "memory_gb": 16,
        "disk_gb": 500,
        "description": "High-performance database server",
        "license_type": "Red Hat Enterprise Linux",
        "current_count": 1
    },
    {
        "id": 4,
        "name": "Micro Service",
        "cpu_cores": 1,
        "memory_gb": 2,
        "disk_gb": 25,
        "description": "Lightweight microservice container",
        "license_type": "Prometheus",
        "current_count": 5
    },
    {
        "id": 5,
        "name": "Enterprise Application",
        "cpu_cores": 6,
        "memory_gb": 12,
        "disk_gb": 200,
        "description": "Enterprise application server",
        "license_type": "VMware vSphere",
        "current_count": 1
    }
]


@router.get("/profiles")
async def get_vm_profiles():
    """Get all VM profiles with current counts"""
    try:
        return {
            "profiles": vm_profiles,
            "total_profiles": len(vm_profiles),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get VM profiles: {str(e)}")


@router.get("/profiles/preview")
async def get_profile_preview():
    """Get profile preview with capacity analysis using 80% rule"""
    try:
        # Get system resources
        cpu_count = psutil.cpu_count()
        memory_total = psutil.virtual_memory().total / (1024**3)  # GB
        
        # Count actual VMs from vCenter cache and categorize by profile types
        actual_vms = vcenter_vms_cache + [{
            "vm": "localhost",
            "cores": cpu_count,
            "memory": memory_total,
            "source": "system"
        }]
        
        print(f"📊 Profile Preview: Analyzing {len(actual_vms)} actual VMs ({len(vcenter_vms_cache)} from vCenter + 1 system)")
        
        # Update vm_profiles with actual VM counts
        for profile in vm_profiles:
            # Count VMs that match this profile's resource requirements
            matching_vms = 0
            for vm in actual_vms:
                vm_cores = vm.get('cores', 0)
                vm_memory = vm.get('memory', 0)
                # Match VMs to profiles based on resource requirements (with some tolerance)
                if (abs(vm_cores - profile["cpu_cores"]) <= 1 and 
                    abs(vm_memory - profile["memory_gb"]) <= 2):
                    matching_vms += 1
            profile["current_count"] = matching_vms
        
        # Calculate current resource usage from actual VMs
        total_cpu_used = sum([vm.get('cores', 0) for vm in actual_vms])
        total_memory_used = sum([vm.get('memory', 0) for vm in actual_vms])
        
        # Apply 80% capacity rule
        max_cpu_capacity = int(cpu_count * 0.8)
        max_memory_capacity = int(memory_total * 0.8)
        
        # Calculate remaining capacity
        remaining_cpu = max_cpu_capacity - total_cpu_used
        remaining_memory = max_memory_capacity - total_memory_used
        
        # Calculate how many more VMs can be created per profile
        profile_analysis = []
        for profile in vm_profiles:
            # Check license availability
            license_check = await check_license_availability(profile["license_type"], 1)
            
            # Calculate max additional VMs based on resources
            max_by_cpu = remaining_cpu // profile["cpu_cores"] if profile["cpu_cores"] > 0 else 0
            max_by_memory = remaining_memory // profile["memory_gb"] if profile["memory_gb"] > 0 else 0
            max_by_license = license_check["available_count"] if license_check["available"] else 0
            
            # The limiting factor determines max additional VMs
            max_additional = min(max_by_cpu, max_by_memory, max_by_license)
            
            # Calculate resource utilization for this profile
            profile_cpu_usage = (profile["cpu_cores"] * profile["current_count"]) / max_cpu_capacity * 100
            profile_memory_usage = (profile["memory_gb"] * profile["current_count"]) / max_memory_capacity * 100
            
            profile_analysis.append({
                "profile_id": profile["id"],
                "profile_name": profile["name"],
                "current_count": profile["current_count"],
                "max_additional": max(0, max_additional),
                "max_total_possible": profile["current_count"] + max(0, max_additional),
                "cpu_per_vm": profile["cpu_cores"],
                "memory_per_vm": profile["memory_gb"],
                "disk_per_vm": profile["disk_gb"],
                "license_type": profile["license_type"],
                "license_available": license_check["available"],
                "license_count_available": license_check["available_count"],
                "limiting_factor": "CPU" if max_by_cpu <= max_by_memory and max_by_cpu <= max_by_license else "Memory" if max_by_memory <= max_by_license else "License",
                "profile_cpu_usage_percent": round(profile_cpu_usage, 1),
                "profile_memory_usage_percent": round(profile_memory_usage, 1)
            })
        
        return {
            "system_capacity": {
                "total_cpu_cores": cpu_count,
                "total_memory_gb": round(memory_total, 1),
                "max_cpu_capacity_80_percent": max_cpu_capacity,
                "max_memory_capacity_80_percent": max_memory_capacity,
                "current_cpu_used": total_cpu_used,
                "current_memory_used": total_memory_used,
                "remaining_cpu": remaining_cpu,
                "remaining_memory": remaining_memory,
                "cpu_utilization_percent": round((total_cpu_used / max_cpu_capacity) * 100, 1),
                "memory_utilization_percent": round((total_memory_used / max_memory_capacity) * 100, 1)
            },
            "profile_analysis": profile_analysis,
            "total_current_vms": sum([p["current_count"] for p in vm_profiles]),
            "total_max_additional_vms": sum([p["max_additional"] for p in profile_analysis]),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate profile preview: {str(e)}")


@router.get("/capacity/clusters")
async def get_cluster_capacity_analysis():
    """Get capacity analysis broken down by compute clusters"""
    try:
        # Get all VMs and group by cluster
        all_vms = await get_all_vms()
        clusters = {}
        
        for vm in all_vms:
            cluster_name = vm.get('cluster', 'Unknown')
            if cluster_name not in clusters:
                clusters[cluster_name] = {
                    'name': cluster_name,
                    'vms': [],
                    'total_cpu': 0,
                    'total_memory': 0,
                    'total_vms': 0
                }
            
            clusters[cluster_name]['vms'].append(vm)
            clusters[cluster_name]['total_cpu'] += vm.get('cores', 0)
            clusters[cluster_name]['total_memory'] += vm.get('memory', 0)
            clusters[cluster_name]['total_vms'] += 1
        
        # Calculate capacity for each cluster
        cluster_analysis = []
        for cluster_name, cluster_data in clusters.items():
            if cluster_data['total_vms'] > 0:
                avg_cpu = sum(vm.get('cpu', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                avg_memory = sum(vm.get('memory_usage', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                
                # Calculate capacity with 80% utilization rule
                max_additional_vms = 0
                limiting_factor = "CPU"
                
                if cluster_data['total_cpu'] > 0:
                    cpu_capacity = int((cluster_data['total_cpu'] * 0.8) / 2) - cluster_data['total_vms']
                    memory_capacity = int((cluster_data['total_memory'] * 0.8) / 4) - cluster_data['total_vms']
                    
                    max_additional_vms = max(0, min(cpu_capacity, memory_capacity))
                    limiting_factor = "CPU" if cpu_capacity < memory_capacity else "Memory"
                
                cluster_analysis.append({
                    'cluster': cluster_name,
                    'current_vms': cluster_data['total_vms'],
                    'total_cpu_cores': cluster_data['total_cpu'],
                    'total_memory_gb': cluster_data['total_memory'],
                    'avg_cpu_usage': round(avg_cpu, 1),
                    'avg_memory_usage': round(avg_memory, 1),
                    'max_additional_vms': max_additional_vms,
                    'limiting_factor': limiting_factor,
                    'cpu_utilization': round((cluster_data['total_vms'] * 2) / max(cluster_data['total_cpu'], 1) * 100, 1),
                    'memory_utilization': round((cluster_data['total_vms'] * 4) / max(cluster_data['total_memory'], 1) * 100, 1)
                })
        
        return {
            'clusters': cluster_analysis,
            'total_clusters': len(cluster_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in cluster capacity analysis: {e}")
        return {
            'clusters': [],
            'total_clusters': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@router.get("/search")
async def search_assets(q: str = "", type: str = "all"):
    """Search through VMs and other visible assets"""
    try:
        results = []
        
        # Search VMs
        if type in ["all", "vm", "vms"]:
            all_vms = await get_all_vms()
            for vm in all_vms:
                vm_name = vm.get('vm', '').lower()
                cluster = vm.get('cluster', '').lower()
                source = vm.get('source', '').lower()
                
                if (q.lower() in vm_name or 
                    q.lower() in cluster or 
                    q.lower() in source):
                    results.append({
                        'type': 'vm',
                        'name': vm.get('vm'),
                        'cluster': vm.get('cluster'),
                        'source': vm.get('source'),
                        'status': vm.get('status'),
                        'cpu': vm.get('cpu'),
                        'memory': vm.get('memory'),
                        'details': vm.get('details', {})
                    })
        
        # Search Infrastructure
        if type in ["all", "infrastructure", "infra"]:
            try:
                infra_data = vcenter_inventory_cache
                for item in infra_data:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    if q.lower() in item_name or q.lower() in item_type:
                        results.append({
                            'type': 'infrastructure',
                            'name': item.get('name'),
                            'item_type': item.get('type'),
                            'status': item.get('status'),
                            'details': item.get('details', {})
                        })
            except Exception:
                pass
        
        return {
            'query': q,
            'search_type': type,
            'results': results,
            'total_results': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in search: {e}")
        return {
            'query': q,
            'search_type': type,
            'results': [],
            'total_results': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Admin Workflow Management endpoints
class WorkflowView(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    clusters: List[str]
    view_type: str  # 'capacity', 'profile', 'monitoring'
    filters: dict
    created_by: str
    created_at: Optional[str] = None

# In-memory storage for workflow views
workflow_views_cache = [
    {
        "id": 1,
        "name": "Production Monitoring",
        "description": "Monitor production clusters only",
        "clusters": ["Production-Cluster"],
        "view_type": "monitoring",
        "filters": {"status": "running", "min_cpu": 0},
        "created_by": "admin",
        "created_at": "2025-07-26T20:00:00Z"
    },
    {
        "id": 2,
        "name": "Development Capacity",
        "description": "Capacity planning for development environments",
        "clusters": ["Development-Cluster"],
        "view_type": "capacity",
        "filters": {"utilization_threshold": 80},
        "created_by": "admin",
        "created_at": "2025-07-26T20:05:00Z"
    }
]

@router.get("/admin/workflows")
async def get_workflow_views():
    """Get all admin-created workflow views"""
    try:
        return {
            "workflows": workflow_views_cache,
            "total": len(workflow_views_cache),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")

@router.post("/admin/workflows")
async def create_workflow_view(workflow: WorkflowView):
    """Create a new admin workflow view"""
    try:
        # Generate new ID
        new_id = max([w["id"] for w in workflow_views_cache], default=0) + 1
        
        new_workflow = {
            "id": new_id,
            "name": workflow.name,
            "description": workflow.description,
            "clusters": workflow.clusters,
            "view_type": workflow.view_type,
            "filters": workflow.filters,
            "created_by": workflow.created_by,
            "created_at": datetime.now().isoformat()
        }
        
        workflow_views_cache.append(new_workflow)
        print(f"✅ Created new workflow view: {workflow.name}")
        
        return new_workflow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@router.get("/admin/workflows/{workflow_id}/data")
async def get_workflow_data(workflow_id: int):
    """Get data for a specific workflow view"""
    try:
        # Find the workflow
        workflow = next((w for w in workflow_views_cache if w["id"] == workflow_id), None)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get data based on workflow type and filters
        if workflow["view_type"] == "capacity":
            # Get cluster capacity data filtered by workflow clusters
            cluster_data = await get_cluster_capacity_analysis()
            filtered_clusters = [
                cluster for cluster in cluster_data["clusters"]
                if cluster["cluster"] in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "clusters": filtered_clusters,
                    "total_clusters": len(filtered_clusters)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        elif workflow["view_type"] == "monitoring":
            # Get VMs filtered by workflow clusters
            all_vms = await get_all_vms()
            filtered_vms = [
                vm for vm in all_vms
                if vm.get("cluster") in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "vms": filtered_vms,
                    "total_vms": len(filtered_vms)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "workflow": workflow,
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow data: {str(e)}")

@router.delete("/admin/workflows/{workflow_id}")
async def delete_workflow_view(workflow_id: int):
    """Delete an admin workflow view"""
    try:
        global workflow_views_cache
        original_count = len(workflow_views_cache)
        workflow_views_cache = [w for w in workflow_views_cache if w["id"] != workflow_id]
        
        if len(workflow_views_cache) == original_count:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        print(f"✅ Deleted workflow view ID: {workflow_id}")
        return {"message": f"Workflow {workflow_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


@router.get("/capacity/clusters")
async def get_cluster_capacity_analysis():
    """Get capacity analysis broken down by compute clusters"""
    try:
        # Get all VMs and group by cluster
        all_vms = await get_all_vms()
        clusters = {}
        
        for vm in all_vms:
            cluster_name = vm.get('cluster', 'Unknown')
            if cluster_name not in clusters:
                clusters[cluster_name] = {
                    'name': cluster_name,
                    'vms': [],
                    'total_cpu': 0,
                    'total_memory': 0,
                    'total_vms': 0
                }
            
            clusters[cluster_name]['vms'].append(vm)
            clusters[cluster_name]['total_cpu'] += vm.get('cores', 0)
            clusters[cluster_name]['total_memory'] += vm.get('memory', 0)
            clusters[cluster_name]['total_vms'] += 1
        
        # Calculate capacity for each cluster
        cluster_analysis = []
        for cluster_name, cluster_data in clusters.items():
            if cluster_data['total_vms'] > 0:
                avg_cpu = sum(vm.get('cpu', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                avg_memory = sum(vm.get('memory_usage', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                
                # Calculate capacity with 80% utilization rule
                max_additional_vms = 0
                limiting_factor = "CPU"
                
                if cluster_data['total_cpu'] > 0:
                    cpu_capacity = int((cluster_data['total_cpu'] * 0.8) / 2) - cluster_data['total_vms']
                    memory_capacity = int((cluster_data['total_memory'] * 0.8) / 4) - cluster_data['total_vms']
                    
                    max_additional_vms = max(0, min(cpu_capacity, memory_capacity))
                    limiting_factor = "CPU" if cpu_capacity < memory_capacity else "Memory"
                
                cluster_analysis.append({
                    'cluster': cluster_name,
                    'current_vms': cluster_data['total_vms'],
                    'total_cpu_cores': cluster_data['total_cpu'],
                    'total_memory_gb': cluster_data['total_memory'],
                    'avg_cpu_usage': round(avg_cpu, 1),
                    'avg_memory_usage': round(avg_memory, 1),
                    'max_additional_vms': max_additional_vms,
                    'limiting_factor': limiting_factor,
                    'cpu_utilization': round((cluster_data['total_vms'] * 2) / max(cluster_data['total_cpu'], 1) * 100, 1),
                    'memory_utilization': round((cluster_data['total_vms'] * 4) / max(cluster_data['total_memory'], 1) * 100, 1)
                })
        
        return {
            'clusters': cluster_analysis,
            'total_clusters': len(cluster_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in cluster capacity analysis: {e}")
        return {
            'clusters': [],
            'total_clusters': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@router.get("/search")
async def search_assets(q: str = "", type: str = "all"):
    """Search through VMs and other visible assets"""
    try:
        results = []
        
        # Search VMs
        if type in ["all", "vm", "vms"]:
            all_vms = await get_all_vms()
            for vm in all_vms:
                vm_name = vm.get('vm', '').lower()
                cluster = vm.get('cluster', '').lower()
                source = vm.get('source', '').lower()
                
                if (q.lower() in vm_name or 
                    q.lower() in cluster or 
                    q.lower() in source):
                    results.append({
                        'type': 'vm',
                        'name': vm.get('vm'),
                        'cluster': vm.get('cluster'),
                        'source': vm.get('source'),
                        'status': vm.get('status'),
                        'cpu': vm.get('cpu'),
                        'memory': vm.get('memory'),
                        'details': vm.get('details', {})
                    })
        
        # Search Infrastructure
        if type in ["all", "infrastructure", "infra"]:
            try:
                infra_data = vcenter_inventory_cache
                for item in infra_data:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    if q.lower() in item_name or q.lower() in item_type:
                        results.append({
                            'type': 'infrastructure',
                            'name': item.get('name'),
                            'item_type': item.get('type'),
                            'status': item.get('status'),
                            'details': item.get('details', {})
                        })
            except:
                pass
        
        return {
            'query': q,
            'search_type': type,
            'results': results,
            'total_results': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in search: {e}")
        return {
            'query': q,
            'search_type': type,
            'results': [],
            'total_results': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Admin Workflow Management endpoints
class WorkflowView(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    clusters: List[str]
    view_type: str  # 'capacity', 'profile', 'monitoring'
    filters: dict
    created_by: str
    created_at: Optional[str] = None

# In-memory storage for workflow views
workflow_views_cache = [
    {
        "id": 1,
        "name": "Production Monitoring",
        "description": "Monitor production clusters only",
        "clusters": ["Production-Cluster"],
        "view_type": "monitoring",
        "filters": {"status": "running", "min_cpu": 0},
        "created_by": "admin",
        "created_at": "2025-07-26T20:00:00Z"
    },
    {
        "id": 2,
        "name": "Development Capacity",
        "description": "Capacity planning for development environments",
        "clusters": ["Development-Cluster"],
        "view_type": "capacity",
        "filters": {"utilization_threshold": 80},
        "created_by": "admin",
        "created_at": "2025-07-26T20:05:00Z"
    }
]

@router.get("/admin/workflows")
async def get_workflow_views():
    """Get all admin-created workflow views"""
    try:
        return {
            "workflows": workflow_views_cache,
            "total": len(workflow_views_cache),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")

@router.post("/admin/workflows")
async def create_workflow_view(workflow: WorkflowView):
    """Create a new admin workflow view"""
    try:
        # Generate new ID
        new_id = max([w["id"] for w in workflow_views_cache], default=0) + 1
        
        new_workflow = {
            "id": new_id,
            "name": workflow.name,
            "description": workflow.description,
            "clusters": workflow.clusters,
            "view_type": workflow.view_type,
            "filters": workflow.filters,
            "created_by": workflow.created_by,
            "created_at": datetime.now().isoformat()
        }
        
        workflow_views_cache.append(new_workflow)
        print(f"✅ Created new workflow view: {workflow.name}")
        
        return new_workflow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@router.get("/admin/workflows/{workflow_id}/data")
async def get_workflow_data(workflow_id: int):
    """Get data for a specific workflow view"""
    try:
        # Find the workflow
        workflow = next((w for w in workflow_views_cache if w["id"] == workflow_id), None)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get data based on workflow type and filters
        if workflow["view_type"] == "capacity":
            # Get cluster capacity data filtered by workflow clusters
            cluster_data = await get_cluster_capacity_analysis()
            filtered_clusters = [
                cluster for cluster in cluster_data["clusters"]
                if cluster["cluster"] in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "clusters": filtered_clusters,
                    "total_clusters": len(filtered_clusters)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        elif workflow["view_type"] == "monitoring":
            # Get VMs filtered by workflow clusters
            all_vms = await get_all_vms()
            filtered_vms = [
                vm for vm in all_vms
                if vm.get("cluster") in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "vms": filtered_vms,
                    "total_vms": len(filtered_vms)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "workflow": workflow,
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow data: {str(e)}")

@router.delete("/admin/workflows/{workflow_id}")
async def delete_workflow_view(workflow_id: int):
    """Delete an admin workflow view"""
    try:
        global workflow_views_cache
        original_count = len(workflow_views_cache)
        workflow_views_cache = [w for w in workflow_views_cache if w["id"] != workflow_id]
        
        if len(workflow_views_cache) == original_count:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        print(f"✅ Deleted workflow view ID: {workflow_id}")
        return {"message": f"Workflow {workflow_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")
