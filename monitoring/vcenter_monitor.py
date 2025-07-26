
from pyVim.connect import SmartConnectNoSSL, Disconnect
from pyVmomi import vim
from datetime import datetime
from db.init import SessionLocal
from db.models import VirtualMachine, VMMetric
import atexit

def fetch_vcenter_metrics(host, user, pwd, port=443):
    si = SmartConnectNoSSL(host=host, user=user, pwd=pwd, port=port)
    atexit.register(Disconnect, si)
    content = si.RetrieveContent()

    db = SessionLocal()
    now = datetime.utcnow()

    try:
        for datacenter in content.rootFolder.childEntity:
            for vm in datacenter.vmFolder.childEntity:
                if isinstance(vm, vim.VirtualMachine):
                    name = vm.name
                    summary = vm.summary
                    quick_stats = summary.quickStats

                    cpu_usage = quick_stats.overallCpuUsage or 0
                    memory_usage = quick_stats.guestMemoryUsage or 0
                    cpu_cores = summary.config.numCpu or 1
                    memory_gb = summary.config.memorySizeMB / 1024 if summary.config else 0

                    vm_record = db.query(VirtualMachine).filter_by(name=name).first()
                    if not vm_record:
                        vm_record = VirtualMachine(
                            name=name,
                            cluster=datacenter.name,
                            cpu_cores=cpu_cores,
                            memory_gb=memory_gb,
                            disk_gb=100
                        )
                        db.add(vm_record)
                        db.commit()
                        db.refresh(vm_record)

                    metric = VMMetric(
                        vm_id=vm_record.id,
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        disk_io=0.0,
                        net_io=0.0,
                        timestamp=now
                    )
                    db.add(metric)
        db.commit()
    except Exception as e:
        print(f"Error fetching from vCenter: {e}")
        db.rollback()
    finally:
        db.close()
        Disconnect(si)

# Example usage (replace with your real vCenter details)
if __name__ == "__main__":
    fetch_vcenter_metrics("vcenter.example.com", "admin", "password")
