#!/usr/bin/env python3

import psutil
import subprocess
import json
import time
from datetime import datetime, timezone
from db.init import get_session
from db.models import VirtualMachine, VMMetric

class MacSystemMonitor:
    """Monitor Mac system resources and simulate VM data for IROA"""
    
    def __init__(self):
        self.session = get_session()
        
    def get_system_info(self):
        """Get basic system information"""
        try:
            # Get system info using system_profiler
            result = subprocess.run(['system_profiler', 'SPHardwareDataType', '-json'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                hardware = data['SPHardwareDataType'][0]
                return {
                    'model': hardware.get('machine_model', 'Unknown Mac'),
                    'cpu': hardware.get('cpu_type', 'Unknown CPU'),
                    'memory': hardware.get('physical_memory', 'Unknown'),
                    'serial': hardware.get('serial_number', 'Unknown')
                }
        except Exception as e:
            print(f"Error getting system info: {e}")
            
        return {
            'model': 'Mac System',
            'cpu': 'Apple Silicon',
            'memory': f"{psutil.virtual_memory().total // (1024**3)}GB",
            'serial': 'MAC001'
        }
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self):
        """Get current memory usage percentage"""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def get_disk_usage(self):
        """Get disk usage for root partition"""
        disk = psutil.disk_usage('/')
        return (disk.used / disk.total) * 100
    
    def get_network_stats(self):
        """Get network I/O statistics"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    def get_process_info(self):
        """Get top processes by CPU usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 0:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and return top 10
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
    
    def create_virtual_vms(self):
        """Create virtual VMs based on running processes to simulate virtualization"""
        processes = self.get_process_info()
        system_info = self.get_system_info()
        
        # Create or update VM records based on top processes
        vm_count = 0
        for i, proc in enumerate(processes[:5]):  # Top 5 processes as VMs
            vm_count += 1
            vm_name = f"mac-vm-{vm_count:02d}-{proc['name'][:10]}"
            
            # Check if VM already exists
            existing_vm = self.session.query(VirtualMachine).filter_by(name=vm_name).first()
            
            if not existing_vm:
                vm = VirtualMachine(
                    name=vm_name,
                    cluster=f"Mac-Cluster-{system_info['model'][:10]}",
                    host=system_info['model'],
                    cpu_cores=max(1, int(psutil.cpu_count() * (proc['cpu_percent'] / 100))),
                    memory_gb=max(1, int(8 * (proc['memory_percent'] / 100))),  # Assume 8GB base
                    status='running' if proc['cpu_percent'] > 1 else 'idle'
                )
                self.session.add(vm)
                self.session.commit()
                print(f"Created VM: {vm_name}")
            else:
                # Update existing VM status
                existing_vm.status = 'running' if proc['cpu_percent'] > 1 else 'idle'
                self.session.commit()
    
    def collect_metrics(self):
        """Collect current system metrics and store as VM metrics"""
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        disk_usage = self.get_disk_usage()
        network = self.get_network_stats()
        
        print("🖥️  Mac System Metrics:")
        print(f"   CPU Usage: {cpu_usage:.1f}%")
        print(f"   Memory Usage: {memory_usage:.1f}%")
        print(f"   Disk Usage: {disk_usage:.1f}%")
        print(f"   Network: {network['bytes_sent']//1024//1024}MB sent, {network['bytes_recv']//1024//1024}MB received")
        
        # Get all VMs and create metrics for them
        vms = self.session.query(VirtualMachine).all()
        
        for vm in vms:
            # Simulate VM-specific metrics based on system load
            vm_cpu = min(100, cpu_usage + (hash(vm.name) % 20 - 10))  # Add some variance
            vm_memory = min(100, memory_usage + (hash(vm.name) % 15 - 7))
            vm_disk = min(100, disk_usage + (hash(vm.name) % 10 - 5))
            
            metric = VMMetric(
                vm_id=vm.id,
                timestamp=datetime.now(timezone.utc),
                cpu_usage=max(0, vm_cpu),
                memory_usage=max(0, vm_memory),
                disk_usage=max(0, vm_disk),
                network_in=network['bytes_recv'] // len(vms),  # Distribute network load
                network_out=network['bytes_sent'] // len(vms)
            )
            
            self.session.add(metric)
        
        self.session.commit()
        print(f"📊 Stored metrics for {len(vms)} VMs")
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_cpu': cpu_usage,
            'system_memory': memory_usage,
            'system_disk': disk_usage,
            'vm_count': len(vms),
            'network': network
        }
    
    def start_monitoring(self, interval=30):
        """Start continuous monitoring"""
        print(f"🚀 Starting Mac system monitoring (interval: {interval}s)")
        
        # Create initial VMs
        self.create_virtual_vms()
        
        try:
            while True:
                self.collect_metrics()
                print(f"⏰ Next collection in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        finally:
            self.session.close()

def main():
    """Main function to run the Mac monitor"""
    monitor = MacSystemMonitor()
    
    # Show system info
    system_info = monitor.get_system_info()
    print("🍎 Mac System Monitor for IROA")
    print(f"   Model: {system_info['model']}")
    print(f"   CPU: {system_info['cpu']}")
    print(f"   Memory: {system_info['memory']}")
    print("-" * 50)
    
    # Create VMs and start monitoring
    monitor.start_monitoring(interval=30)

if __name__ == "__main__":
    main()
