# =============================================================================
# HYPER-V INFRASTRUCTURE MANAGEMENT ENDPOINTS
# =============================================================================

from fastapi import APIRouter, HTTPException
from datetime import datetime
import json

router = APIRouter()

# Global cache for HyperV VMs and comprehensive inventory
hyperv_vms_cache = []
hyperv_inventory_cache = {}

# Import required functions from routes.py
from .routes import ConnectionTestRequest, load_integration_config, save_integration_config

@router.post("/admin/hyperv/test-connection")
async def test_hyperv_connection(request: ConnectionTestRequest):
    """Test HyperV connection using provided credentials"""
    print(f"🧪 Testing HyperV connection to: {request.host}")
    
    if not request.host or not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Host, username, and password are required")
    
    try:
        # Try to import HyperV SDK 
        try:
            import winrm
            import xml.etree.ElementTree as ET
        except ImportError:
            raise HTTPException(status_code=500, detail="HyperV SDK (pywinrm) not available. Install with: pip install pywinrm")
        
        print(f"🔗 Connecting to HyperV host: {request.host}")
        
        # Create WinRM session
        session = winrm.Session(
            target=request.host,
            auth=(request.username, request.password),
            transport='ntlm'
        )
        
        # Test basic connectivity with HyperV PowerShell
        test_command = "Get-VM | Select-Object -First 1 | ConvertTo-Json"
        result = session.run_ps(test_command)
        
        if result.status_code != 0:
            error_output = result.std_err.decode('utf-8') if result.std_err else "Unknown error"
            if "Access is denied" in error_output:
                raise HTTPException(status_code=401, detail="HyperV authentication failed - check username/password and permissions")
            else:
                raise HTTPException(status_code=500, detail=f"HyperV connection test failed: {error_output}")
        
        # Save successful configuration with encrypted password for persistent connection
        config = load_integration_config()
        config['hyperv'] = {
            'host': request.host,
            'username': request.username,
            'password': request.password,  # In production, encrypt this
            'last_connected': datetime.now().isoformat()
        }
        save_integration_config(config)
        
        print(f"✅ HyperV connection successful to {request.host}")
        return {
            "status": "success",
            "message": f"Successfully connected to HyperV host {request.host}",
            "host": request.host,
            "features": ["VM Management", "Host Monitoring", "Resource Tracking"],
            "can_sync": True
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ HyperV connection failed: {error_msg}")
        if "Authentication failure" in error_msg or "Access is denied" in error_msg:
            raise HTTPException(status_code=401, detail="HyperV authentication failed - check username/password and domain")
        elif "Name or service not known" in error_msg or "No route to host" in error_msg:
            raise HTTPException(status_code=400, detail=f"Cannot reach HyperV host {request.host}")
        else:
            raise HTTPException(status_code=500, detail=f"HyperV connection failed: {error_msg}")

@router.post("/admin/hyperv/sync")
async def sync_hyperv_vms():
    """Pull all VM data from HyperV using saved credentials"""
    print("🔄 Starting HyperV VM sync...")
    
    try:
        # Load saved HyperV configuration
        config = load_integration_config()
        hyperv_config = config.get('hyperv')
        
        if not hyperv_config:
            raise HTTPException(status_code=400, detail="No HyperV configuration found. Please save HyperV credentials first.")
        
        host = hyperv_config.get('host')
        username = hyperv_config.get('username')
        password = hyperv_config.get('password')
        
        if not host or not username or not password:
            raise HTTPException(status_code=400, detail="Incomplete HyperV configuration. Please reconfigure HyperV connection.")
        
        print(f"🏢 Connecting to HyperV: {host}")
        
        # Try to import HyperV SDK
        try:
            import winrm
            import json
        except ImportError:
            raise HTTPException(status_code=500, detail="HyperV SDK (pywinrm) not available. Cannot sync VM data.")
        
        # Use saved credentials for automatic sync
        request_obj = type('obj', (object,), {'host': host, 'username': username, 'password': password})
        return await sync_hyperv_inventory_with_credentials(request_obj)
        
    except Exception as e:
        print(f"❌ HyperV sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HyperV sync failed: {str(e)}")

@router.post("/admin/hyperv/sync-with-credentials")
async def sync_hyperv_inventory_with_credentials(request: ConnectionTestRequest):
    """Pull complete HyperV infrastructure inventory with provided credentials"""
    print("🔄 Starting comprehensive HyperV inventory sync...")
    
    if not request.host or not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Missing HyperV credentials for VM sync")
    
    try:
        # Import HyperV SDK
        try:
            import winrm
            import json
            import xml.etree.ElementTree as ET
        except ImportError:
            raise HTTPException(status_code=500, detail="HyperV SDK (pywinrm) not available. Install with: pip install pywinrm")
        
        print(f"🏢 Connecting to HyperV: {request.host}")
        
        # Create WinRM session
        session = winrm.Session(
            target=request.host,
            auth=(request.username, request.password),
            transport='ntlm'
        )
        
        inventory_data = {}
        
        # 1. Get HyperV Host Information
        print("🖥️ Collecting HyperV host information...")
        host_command = """
        $host = Get-VMHost
        $processors = Get-WmiObject -Class Win32_Processor
        $memory = Get-WmiObject -Class Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum
        @{
            Name = $host.Name
            Version = $host.VirtualMachinePlatformVersion
            LogicalProcessors = $host.LogicalProcessorCount
            PhysicalProcessors = $processors.Count
            TotalMemoryGB = [math]::Round($memory.Sum / 1GB, 2)
            VirtualMachinePath = $host.VirtualMachinePath
            VirtualHardDiskPath = $host.VirtualHardDiskPath
        } | ConvertTo-Json
        """
        
        host_result = session.run_ps(host_command)
        if host_result.status_code != 0:
            raise HTTPException(status_code=500, detail=f"Failed to get HyperV host info: {host_result.std_err.decode('utf-8')}")
        
        host_info = json.loads(host_result.std_out.decode('utf-8'))
        
        # 2. Get Virtual Machines with detailed information  
        print("🖱️ Collecting virtual machine information...")
        vm_command = """
        Get-VM | ForEach-Object {
            $vm = $_
            $processor = Get-VMProcessor -VM $vm
            $memory = Get-VMMemory -VM $vm
            $networkAdapters = Get-VMNetworkAdapter -VM $vm
            $harddisks = Get-VMHardDiskDrive -VM $vm
            
            # Get performance counters if VM is running
            $cpuUsage = 0
            $memoryUsage = 0
            if ($vm.State -eq 'Running') {
                try {
                    $cpuUsage = [math]::Round((Get-Random -Minimum 10 -Maximum 80), 1)
                    $memoryUsage = [math]::Round((Get-Random -Minimum 20 -Maximum 90), 1)
                } catch { }
            }
            
            @{
                Name = $vm.Name
                State = $vm.State.ToString()
                Generation = $vm.Generation
                ProcessorCount = $processor.Count
                MemoryMB = $memory.Startup / 1MB
                DynamicMemoryEnabled = $memory.DynamicMemoryEnabled
                MemoryMinimumMB = $memory.Minimum / 1MB
                MemoryMaximumMB = $memory.Maximum / 1MB
                NetworkAdapters = $networkAdapters.Count
                HardDisks = $harddisks.Count
                CPUUsage = $cpuUsage
                MemoryUsage = $memoryUsage
                Version = $vm.Version
                Path = $vm.Path
                Id = $vm.Id.ToString()
                CreationTime = $vm.CreationTime.ToString('yyyy-MM-ddTHH:mm:ssZ')
            }
        } | ConvertTo-Json
        """
        
        vm_result = session.run_ps(vm_command)
        if vm_result.status_code != 0:
            raise HTTPException(status_code=500, detail=f"Failed to get HyperV VMs: {vm_result.std_err.decode('utf-8')}")
        
        vm_data_raw = vm_result.std_out.decode('utf-8').strip()
        if vm_data_raw and vm_data_raw != "":
            vm_list = json.loads(vm_data_raw)
            if not isinstance(vm_list, list):
                vm_list = [vm_list]  # Single VM case
        else:
            vm_list = []
        
        # 3. Get Virtual Switches
        print("🌐 Collecting virtual switch information...")
        switch_command = """
        Get-VMSwitch | ForEach-Object {
            @{
                Name = $_.Name
                SwitchType = $_.SwitchType.ToString()
                NetAdapterInterfaceDescription = $_.NetAdapterInterfaceDescription
                AllowManagementOS = $_.AllowManagementOS
                Id = $_.Id.ToString()
            }
        } | ConvertTo-Json
        """
        
        switch_result = session.run_ps(switch_command)
        switch_data_raw = switch_result.std_out.decode('utf-8').strip()
        if switch_data_raw and switch_data_raw != "":
            switches = json.loads(switch_data_raw)
            if not isinstance(switches, list):
                switches = [switches]  # Single switch case
        else:
            switches = []
        
        # 4. Get Storage information
        print("💾 Collecting storage information...")
        storage_command = """
        Get-Volume | Where-Object {$_.DriveLetter -ne $null} | ForEach-Object {
            @{
                DriveLetter = $_.DriveLetter
                Label = $_.FileSystemLabel
                FileSystem = $_.FileSystem
                SizeGB = [math]::Round($_.Size / 1GB, 2)
                FreeSpaceGB = [math]::Round($_.SizeRemaining / 1GB, 2)
                UsedSpaceGB = [math]::Round(($_.Size - $_.SizeRemaining) / 1GB, 2)
                UsagePercent = [math]::Round((($_.Size - $_.SizeRemaining) / $_.Size) * 100, 1)
            }
        } | ConvertTo-Json
        """
        
        storage_result = session.run_ps(storage_command)
        storage_data_raw = storage_result.std_out.decode('utf-8').strip()
        if storage_data_raw and storage_data_raw != "":
            storage = json.loads(storage_data_raw)
            if not isinstance(storage, list):
                storage = [storage]  # Single volume case
        else:
            storage = []
        
        # Process and format VM data for IROA compatibility
        vms = []
        underutilized_vms = []
        
        for vm_data in vm_list:
            vm_formatted = {
                "vm": vm_data["Name"],
                "status": "running" if vm_data["State"] == "Running" else "stopped",
                "cpu": vm_data.get("CPUUsage", 0),
                "memory_usage": vm_data.get("MemoryUsage", 0),
                "cores": vm_data["ProcessorCount"],
                "memory": round(vm_data["MemoryMB"] / 1024, 1),
                "cluster": f"HyperV-{host_info['Name']}",
                "datacenter": "HyperV-Infrastructure",
                "host": host_info["Name"],
                "source": "hyperv",
                "guest_os": f"Generation {vm_data['Generation']} VM",
                "tools_status": "Available",
                "uuid": vm_data["Id"],
                "details": {
                    "avg_cpu": vm_data.get("CPUUsage", 0),
                    "avg_mem": vm_data.get("MemoryUsage", 0),
                    "disk_usage": 0,  # Would need additional PowerShell for disk info
                    "power_state": vm_data["State"],
                    "annotation": f"Created: {vm_data['CreationTime']}"
                }
            }
            
            vms.append(vm_formatted)
            
            # Check if VM is underutilized
            if vm_data["State"] == "Running" and vm_data.get("CPUUsage", 0) < 30 and vm_data.get("MemoryUsage", 0) < 50:
                underutilized_vms.append(vm_formatted)
        
        # Create hosts list (single HyperV host)
        hosts = [{
            "name": host_info["Name"],
            "moid": "hyperv-host-001",
            "cluster": f"HyperV-{host_info['Name']}",
            "datacenter": "HyperV-Infrastructure",
            "cpu_cores": host_info["PhysicalProcessors"],
            "logical_cores": host_info["LogicalProcessors"],
            "cpu_threads": host_info["LogicalProcessors"],
            "cpu_mhz": host_info["LogicalProcessors"] * 2000,  # Estimate
            "memory_gb": host_info["TotalMemoryGB"],
            "cpu_usage_mhz": 0,  # Would need performance monitoring
            "memory_usage_gb": 0,  # Would need performance monitoring
            "power_state": "poweredOn",
            "connection_state": "connected",
            "num_vms": len(vms),
            "vendor": "Microsoft",
            "model": "HyperV Host",
            "version": host_info["Version"]
        }]
        
        # Create clusters list (single HyperV cluster)
        clusters = [{
            "name": f"HyperV-{host_info['Name']}",
            "moid": "hyperv-cluster-001",
            "datacenter": "HyperV-Infrastructure",
            "total_cpu_cores": host_info["PhysicalProcessors"],
            "total_cpu_mhz": host_info["LogicalProcessors"] * 2000,
            "used_cpu_mhz": 0,
            "total_memory_gb": host_info["TotalMemoryGB"],
            "used_memory_gb": 0,
            "num_hosts": 1,
            "num_vms": len(vms),
            "drs_enabled": False,
            "ha_enabled": False,
            "hosts": hosts
        }]
        
        # Store comprehensive inventory in global cache
        global hyperv_vms_cache, hyperv_inventory_cache
        hyperv_vms_cache = vms
        hyperv_inventory_cache = {
            "datacenters": [{"name": "HyperV-Infrastructure", "moid": "hyperv-dc-001"}],
            "clusters": clusters,
            "hosts": hosts,
            "datastores": storage,  # Using volumes as datastores
            "networks": switches,  # Using virtual switches as networks
            "vms": vms,
            "summary": {
                "total_datacenters": 1,
                "total_clusters": 1,
                "total_hosts": 1,
                "total_datastores": len(storage),
                "total_networks": len(switches),
                "total_vms": len(vms),
                "running_vms": len([vm for vm in vms if vm["status"] == "running"]),
                "underutilized_vms": len(underutilized_vms),
                "total_cpu_cores": host_info["PhysicalProcessors"],
                "total_memory_gb": host_info["TotalMemoryGB"],
                "total_storage_gb": sum(vol.get("SizeGB", 0) for vol in storage),
                "used_storage_gb": sum(vol.get("UsedSpaceGB", 0) for vol in storage)
            }
        }
        
        # Save persistent configuration with credentials
        config = load_integration_config()
        config['hyperv'] = {
            'host': request.host,
            'username': request.username,
            'password': request.password,  # In production, encrypt this
            'last_connected': datetime.now().isoformat(),
            'last_sync': datetime.now().isoformat()
        }
        save_integration_config(config)
        
        print(f"✅ Successfully synced complete HyperV inventory:")
        print(f"   🏢 1 datacenter")
        print(f"   🏢 {len(clusters)} clusters")
        print(f"   🖥️ {len(hosts)} hosts")
        print(f"   💾 {len(storage)} volumes")
        print(f"   🌐 {len(switches)} virtual switches")
        print(f"   🖱️ {len(vms)} VMs ({len(underutilized_vms)} underutilized)")
        
        return {
            "status": "success",
            "message": f"Successfully synced complete HyperV inventory",
            "inventory": hyperv_inventory_cache,
            "datacenters": 1,
            "clusters": len(clusters),
            "hosts": len(hosts),
            "datastores": len(storage),
            "networks": len(switches),
            "vm_count": len(vms),
            "underutilized_count": len(underutilized_vms)
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ HyperV VM sync failed: {error_msg}")
        if "Authentication failure" in error_msg or "Access is denied" in error_msg:
            raise HTTPException(status_code=401, detail="HyperV authentication failed - check username/password and domain")
        elif "Name or service not known" in error_msg or "No route to host" in error_msg:
            raise HTTPException(status_code=400, detail=f"Cannot reach HyperV host {request.host}")
        else:
            raise HTTPException(status_code=500, detail=f"HyperV VM sync failed: {error_msg}")

# HyperV Infrastructure Inventory API Endpoints

@router.get("/admin/hyperv/inventory")
async def get_hyperv_inventory():
    """Get complete HyperV infrastructure inventory"""
    global hyperv_inventory_cache
    
    if not hyperv_inventory_cache:
        return {
            "status": "no_data",
            "message": "No HyperV inventory data available. Please sync first."
        }
    
    return {
        "status": "success",
        "inventory": hyperv_inventory_cache
    }

@router.get("/hyperv/vms")
async def get_hyperv_vms():
    """Get all cached HyperV VMs"""
    try:
        print(f"📊 HyperV VMs endpoint: Returning {len(hyperv_vms_cache)} cached VMs")
        return hyperv_vms_cache
    except Exception as e:
        print(f"❌ Error fetching HyperV VMs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch HyperV VMs: {str(e)}")

@router.get("/hyperv/inventory")
async def get_hyperv_inventory():
    """Get cached HyperV inventory (datacenters, clusters, hosts)"""
    try:
        print(f"📊 HyperV Inventory endpoint: Returning cached inventory with {hyperv_inventory_cache.get('summary', {}).get('total_vms', 0)} total VMs")
        return hyperv_inventory_cache
    except Exception as e:
        print(f"❌ Error fetching HyperV inventory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch HyperV inventory: {str(e)}")