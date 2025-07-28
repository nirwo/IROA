"""
Metrics Collection and Storage Module
Handles collection, storage, and retrieval of historical metrics for forecasting
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self, db_path: str = "database/iroa.db"):
        self.db_path = db_path
        self.ensure_schema()
    
    def ensure_schema(self):
        """Ensure metrics history schema exists"""
        schema_path = Path(__file__).parent.parent / "database" / "metrics_history_schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.db_path)
            try:
                conn.executescript(schema_sql)
                conn.commit()
                logger.info("Metrics history schema initialized")
            except Exception as e:
                logger.error(f"Failed to initialize metrics schema: {e}")
            finally:
                conn.close()
    
    def store_vm_metrics(self, vm_data: Dict) -> bool:
        """Store VM metrics to historical database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Current timestamp
            now = datetime.now().isoformat()
            
            for vm in vm_data.get('vms', []):
                cursor.execute("""
                    INSERT INTO vm_metrics_history (
                        vm_id, vm_name, cluster_name, host_name, datacenter_name,
                        allocated_vcpus, allocated_memory_gb, allocated_storage_gb,
                        cpu_usage_percent, memory_usage_percent, storage_usage_gb,
                        power_state, vm_status, metric_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vm.get('id', vm.get('vm_id', '')),
                    vm.get('name', vm.get('vm', '')),
                    vm.get('cluster', ''),
                    vm.get('host', ''),
                    vm.get('datacenter', ''),
                    vm.get('cores', 0),
                    vm.get('memory', 0),
                    vm.get('storage', 0),
                    vm.get('cpu', 0),
                    vm.get('memory_usage', 0),
                    vm.get('storage_used', 0),
                    vm.get('power_state', 'unknown'),
                    vm.get('status', 'unknown'),
                    now
                ))
            
            conn.commit()
            logger.info(f"Stored metrics for {len(vm_data.get('vms', []))} VMs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store VM metrics: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def store_host_metrics(self, host_data: Dict) -> bool:
        """Store host metrics to historical database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            for host in host_data.get('hosts', []):
                # Calculate allocated vCPUs from VMs on this host
                allocated_vcpus = sum(vm.get('cores', 0) for vm in host_data.get('vms', []) 
                                    if vm.get('host') == host.get('name'))
                
                # Count VMs on this host
                host_vms = [vm for vm in host_data.get('vms', []) if vm.get('host') == host.get('name')]
                running_vms = len([vm for vm in host_vms if vm.get('status') == 'running'])
                
                cursor.execute("""
                    INSERT INTO host_metrics_history (
                        host_id, host_name, cluster_name, datacenter_name,
                        physical_cpu_cores, physical_memory_gb, physical_storage_gb,
                        allocated_vcpus, cpu_usage_percent, memory_usage_percent, 
                        storage_usage_percent, total_vms, running_vms,
                        host_status, metric_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    host.get('id', host.get('name', '')),
                    host.get('name', ''),
                    host.get('cluster', ''),
                    host.get('datacenter', ''),
                    host.get('cpu_cores', 0),
                    host.get('memory_gb', 0),
                    host.get('storage_gb', 0),
                    allocated_vcpus,
                    host.get('cpu_usage', 0),
                    host.get('memory_usage', 0),
                    host.get('storage_usage', 0),
                    len(host_vms),
                    running_vms,
                    host.get('status', 'unknown'),
                    now
                ))
            
            conn.commit()
            logger.info(f"Stored metrics for {len(host_data.get('hosts', []))} hosts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store host metrics: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def store_cluster_metrics(self, cluster_data: Dict) -> bool:
        """Store cluster aggregate metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            for cluster in cluster_data.get('clusters', []):
                cursor.execute("""
                    INSERT INTO cluster_metrics_history (
                        cluster_name, datacenter_name,
                        total_physical_cpu_cores, total_physical_memory_gb, total_physical_storage_gb,
                        total_allocated_vcpus, avg_cpu_usage_percent, avg_memory_usage_percent,
                        avg_storage_usage_percent, total_hosts, connected_hosts,
                        total_vms, running_vms, peak_cpu_usage_percent, peak_memory_usage_percent,
                        metric_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cluster.get('cluster', cluster.get('name', '')),
                    cluster.get('datacenter', ''),
                    cluster.get('physical_cpu_cores', 0),
                    cluster.get('total_memory_gb', 0),
                    cluster.get('total_storage_gb', 0),
                    cluster.get('allocated_vcpus', 0),
                    cluster.get('cpu_utilization', 0),
                    cluster.get('memory_utilization', 0),
                    cluster.get('storage_utilization', 0),
                    cluster.get('host_count', 0),
                    cluster.get('connected_hosts', cluster.get('host_count', 0)),
                    cluster.get('current_vms', 0),
                    cluster.get('running_vms', cluster.get('current_vms', 0)),
                    cluster.get('peak_cpu_usage', cluster.get('cpu_utilization', 0)),
                    cluster.get('peak_memory_usage', cluster.get('memory_utilization', 0)),
                    now
                ))
            
            conn.commit()
            logger.info(f"Stored metrics for {len(cluster_data.get('clusters', []))} clusters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store cluster metrics: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_vm_history(self, vm_id: str, hours: int = 24) -> List[Dict]:
        """Get historical metrics for a specific VM"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM vm_metrics_history 
                WHERE vm_id = ? AND metric_timestamp >= ?
                ORDER BY metric_timestamp ASC
            """, (vm_id, since))
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
            
        except Exception as e:
            logger.error(f"Failed to get VM history: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_cluster_history(self, cluster_name: str, hours: int = 24) -> List[Dict]:
        """Get historical metrics for a cluster"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM cluster_metrics_history 
                WHERE cluster_name = ? AND metric_timestamp >= ?
                ORDER BY metric_timestamp ASC
            """, (cluster_name, since))
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
            
        except Exception as e:
            logger.error(f"Failed to get cluster history: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_forecasting_data(self, resource_type: str, resource_id: str, metric_name: str) -> Optional[Dict]:
        """Get forecasting data for a resource"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM forecasting_aggregates 
                WHERE resource_type = ? AND resource_id = ? AND metric_name = ?
                ORDER BY last_updated DESC LIMIT 1
            """, (resource_type, resource_id, metric_name))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Failed to get forecasting data: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def calculate_forecasting_aggregates(self, resource_type: str, resource_id: str) -> bool:
        """Calculate and store forecasting aggregates for a resource"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determine the source table
            if resource_type == 'vm':
                table = 'vm_metrics_history'
                id_field = 'vm_id'
                metrics = ['cpu_usage_percent', 'memory_usage_percent']
            elif resource_type == 'host':
                table = 'host_metrics_history'
                id_field = 'host_id'
                metrics = ['cpu_usage_percent', 'memory_usage_percent', 'vcpu_allocation_percent']
            elif resource_type == 'cluster':
                table = 'cluster_metrics_history'
                id_field = 'cluster_name'
                metrics = ['avg_cpu_usage_percent', 'avg_memory_usage_percent', 'vcpu_allocation_percent']
            else:
                logger.error(f"Unknown resource type: {resource_type}")
                return False
            
            # Calculate aggregates for each metric
            for metric in metrics:
                # Get data from the last 30 days
                cursor.execute(f"""
                    SELECT {metric}, metric_timestamp 
                    FROM {table} 
                    WHERE {id_field} = ? AND metric_timestamp >= datetime('now', '-30 days')
                    ORDER BY metric_timestamp ASC
                """, (resource_id,))
                
                data = cursor.fetchall()
                if not data:
                    continue
                
                values = [row[0] for row in data]
                timestamps = [datetime.fromisoformat(row[1]) for row in data]
                
                if len(values) < 2:
                    continue
                
                # Calculate basic statistics
                hourly_avg = sum(values) / len(values)
                std_dev = (sum((x - hourly_avg) ** 2 for x in values) / len(values)) ** 0.5
                min_val = min(values)
                max_val = max(values)
                
                # Calculate percentile 95
                sorted_values = sorted(values)
                p95_idx = int(len(sorted_values) * 0.95)
                percentile_95 = sorted_values[p95_idx] if p95_idx < len(sorted_values) else max_val
                
                # Simple linear regression for trend
                n = len(values)
                sum_x = sum(range(n))
                sum_y = sum(values)
                sum_xy = sum(i * values[i] for i in range(n))
                sum_x2 = sum(i * i for i in range(n))
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
                
                # Project forecast (simple linear extrapolation)
                forecast_7d = hourly_avg + (slope * 7 * 24)  # 7 days * 24 hours
                forecast_14d = hourly_avg + (slope * 14 * 24)
                forecast_30d = hourly_avg + (slope * 30 * 24)
                
                # Calculate confidence (inverse of coefficient of variation)
                cv = std_dev / hourly_avg if hourly_avg > 0 else 1
                confidence = max(0, min(100, 100 - (cv * 100)))
                
                # Store the aggregate
                cursor.execute("""
                    INSERT OR REPLACE INTO forecasting_aggregates (
                        resource_type, resource_id, metric_name,
                        hourly_avg, daily_avg, weekly_avg, monthly_avg,
                        growth_rate_daily, std_deviation, min_value, max_value, percentile_95,
                        forecast_7d, forecast_14d, forecast_30d, forecast_confidence,
                        period_start, period_end, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    resource_type, resource_id, metric,
                    hourly_avg, hourly_avg, hourly_avg, hourly_avg,  # Simplified for now
                    slope * 24,  # Daily growth rate
                    std_dev, min_val, max_val, percentile_95,
                    max(0, forecast_7d), max(0, forecast_14d), max(0, forecast_30d), confidence,
                    timestamps[0].isoformat(), timestamps[-1].isoformat(),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            logger.info(f"Calculated forecasting aggregates for {resource_type}:{resource_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to calculate forecasting aggregates: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def store_infrastructure_event(self, event_type: str, severity: str, resource_type: str, 
                                 resource_id: str, resource_name: str, title: str, 
                                 description: str = None) -> bool:
        """Store an infrastructure event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO infrastructure_events (
                    event_type, severity, resource_type, resource_id, resource_name,
                    title, description, event_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_type, severity, resource_type, resource_id, resource_name,
                title, description, datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Stored event: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store event: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_recent_events(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent infrastructure events"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM infrastructure_events 
                WHERE event_timestamp >= ?
                ORDER BY event_timestamp DESC 
                LIMIT ?
            """, (since, limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent events: {e}")
            return []
        finally:
            if conn:
                conn.close()


# Global metrics collector instance
metrics_collector = MetricsCollector()