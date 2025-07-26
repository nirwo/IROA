
from db.init import SessionLocal
from db.models import VMMetric, VirtualMachine
from datetime import datetime

def store_metrics(metrics):
    db = SessionLocal()
    try:
        for metric in metrics:
            vm = db.query(VirtualMachine).filter(VirtualMachine.name == metric['instance']).first()
            if not vm:
                vm = VirtualMachine(name=metric['instance'], cluster="default", cpu_cores=4, memory_gb=8, disk_gb=100)
                db.add(vm)
                db.commit()
                db.refresh(vm)

            vm_metric = VMMetric(
                vm_id=vm.id,
                cpu_usage=metric.get("cpu_usage", 0.0),
                memory_usage=metric.get("memory_usage", 0.0),
                disk_io=metric.get("disk_io", 0.0),
                net_io=metric.get("net_io", 0.0),
                timestamp=metric["timestamp"]
            )
            db.add(vm_metric)
        db.commit()
    except Exception as e:
        print(f"[!] Error storing metrics: {e}")
        db.rollback()
    finally:
        db.close()
