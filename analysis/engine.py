
from db.init import SessionLocal
from db.models import VirtualMachine, VMMetric
from datetime import datetime, timedelta

def get_underutilized_vms(cpu_threshold=10.0, memory_threshold=20.0, days=7):
    db = SessionLocal()
    underutilized = []

    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        vms = db.query(VirtualMachine).all()

        for vm in vms:
            metrics = db.query(VMMetric).filter(
                VMMetric.vm_id == vm.id,
                VMMetric.timestamp >= cutoff
            ).all()

            if not metrics:
                continue

            avg_cpu = sum([m.cpu_usage for m in metrics]) / len(metrics)
            avg_mem = sum([m.memory_usage for m in metrics]) / len(metrics)

            if avg_cpu < cpu_threshold and avg_mem < memory_threshold:
                underutilized.append({
                    "vm": vm.name,
                    "avg_cpu": round(avg_cpu, 2),
                    "avg_mem": round(avg_mem, 2),
                    "cpu_threshold": cpu_threshold,
                    "memory_threshold": memory_threshold
                })
    finally:
        db.close()

    return underutilized
