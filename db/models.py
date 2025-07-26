
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class VirtualMachine(Base):
    __tablename__ = 'virtual_machines'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cluster = Column(String)
    cpu_cores = Column(Integer)
    memory_gb = Column(Float)
    disk_gb = Column(Float)
    is_powered_on = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    metrics = relationship("VMMetric", back_populates="vm")

class VMMetric(Base):
    __tablename__ = 'vm_metrics'

    id = Column(Integer, primary_key=True, index=True)
    vm_id = Column(Integer, ForeignKey('virtual_machines.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_io = Column(Float)
    net_io = Column(Float)

    vm = relationship("VirtualMachine", back_populates="metrics")
