#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.init import engine
from db.models import Base, VirtualMachine, VMMetric
from datetime import datetime, timedelta
import random

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def add_mock_data():
    """Add mock VM data and metrics"""
    from db.init import SessionLocal
    
    db = SessionLocal()
    try:
        # Create mock VMs
        vms = [
            VirtualMachine(name="web-server-01", cluster="prod-cluster", cpu_cores=4, memory_gb=8, disk_gb=100),
            VirtualMachine(name="db-server-01", cluster="prod-cluster", cpu_cores=8, memory_gb=32, disk_gb=500),
            VirtualMachine(name="test-vm-01", cluster="test-cluster", cpu_cores=2, memory_gb=4, disk_gb=50),
            VirtualMachine(name="backup-vm-01", cluster="backup-cluster", cpu_cores=2, memory_gb=4, disk_gb=200),
            VirtualMachine(name="dev-server-01", cluster="dev-cluster", cpu_cores=4, memory_gb=16, disk_gb=100),
        ]
        
        for vm in vms:
            db.add(vm)
        db.commit()
        
        # Create mock metrics for the last 7 days
        for vm in vms:
            for days_ago in range(7):
                for hour in range(0, 24, 2):  # Every 2 hours
                    timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hour)
                    
                    # Generate realistic metrics based on VM type
                    if "test" in vm.name or "backup" in vm.name:
                        # Low utilization VMs
                        cpu_usage = random.uniform(2, 8)
                        memory_usage = random.uniform(10, 25)
                    elif "db" in vm.name:
                        # High utilization DB
                        cpu_usage = random.uniform(60, 85)
                        memory_usage = random.uniform(70, 90)
                    else:
                        # Normal utilization
                        cpu_usage = random.uniform(25, 60)
                        memory_usage = random.uniform(40, 70)
                    
                    metric = VMMetric(
                        vm_id=vm.id,
                        timestamp=timestamp,
                        cpu_usage=cpu_usage,
                        memory_usage=memory_usage,
                        disk_io=random.uniform(10, 100),
                        net_io=random.uniform(5, 50)
                    )
                    db.add(metric)
        
        db.commit()
        print("Mock data added successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing IROA database...")
    create_tables()
    add_mock_data()
    print("Database initialization complete!")
