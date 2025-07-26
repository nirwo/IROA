
import requests
import json
from db.init import SessionLocal
from db.models import VirtualMachine, VMMetric
from datetime import datetime

class ZabbixConnector:
    def __init__(self, url, user, password):
        self.url = url
        self.headers = {"Content-Type": "application/json-rpc"}
        self.auth_token = self.login(user, password)

    def login(self, user, password):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {"user": user, "password": password},
            "id": 1
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        return response.json()["result"]

    def get_hosts(self):
        data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {"output": ["hostid", "host"]},
            "auth": self.auth_token,
            "id": 2
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        return response.json()["result"]

    def get_latest_metric(self, hostid, key_):
        data = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                "hostids": hostid,
                "search": {"key_": key_},
                "sortfield": "name"
            },
            "auth": self.auth_token,
            "id": 3
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        items = response.json().get("result", [])
        return float(items[0]["lastvalue"]) if items else 0.0

    def ingest_zabbix_metrics(self):
        db = SessionLocal()
        try:
            for host in self.get_hosts():
                host_name = host["host"]
                host_id = host["hostid"]
                cpu = self.get_latest_metric(host_id, "system.cpu.util[,idle]")
                mem = self.get_latest_metric(host_id, "vm.memory.size[used]")

                vm = db.query(VirtualMachine).filter_by(name=host_name).first()
                if not vm:
                    vm = VirtualMachine(name=host_name, cluster="zabbix", cpu_cores=2, memory_gb=8, disk_gb=100)
                    db.add(vm)
                    db.commit()
                    db.refresh(vm)

                metric = VMMetric(
                    vm_id=vm.id,
                    cpu_usage=100 - cpu,  # convert idle to used
                    memory_usage=mem / 1024 / 1024 / 1024,  # bytes to GB
                    disk_io=0.0,
                    net_io=0.0,
                    timestamp=datetime.utcnow()
                )
                db.add(metric)
            db.commit()
        except Exception as e:
            print(f"Zabbix ingestion error: {e}")
            db.rollback()
        finally:
            db.close()

# Example usage:
# z = ZabbixConnector("http://your-zabbix-server/api_jsonrpc.php", "Admin", "zabbix")
# z.ingest_zabbix_metrics()
