
from db.init import SessionLocal
from db.models import VirtualMachine, VMMetric
from datetime import datetime, timedelta
import random

def seed_demo_data():
    db = SessionLocal()
    now = datetime.utcnow()

    vm_names = ["vm-alpha", "vm-beta", "vm-gamma"]
    for name in vm_names:
        vm = db.query(VirtualMachine).filter_by(name=name).first()
        if not vm:
            vm = VirtualMachine(name=name, cluster="demo", cpu_cores=4, memory_gb=8, disk_gb=100)
            db.add(vm)
            db.commit()
            db.refresh(vm)

        for i in range(7 * 24):  # 7 days, hourly
            timestamp = now - timedelta(hours=i)
            metric = VMMetric(
                vm_id=vm.id,
                cpu_usage=random.uniform(2, 12),
                memory_usage=random.uniform(10, 30),
                disk_io=random.uniform(5, 50),
                net_io=random.uniform(0.1, 5),
                timestamp=timestamp
            )
            db.add(metric)

    db.commit()
    db.close()
    print("✅ Demo data seeded.")

if __name__ == "__main__":
    seed_demo_data()
