"""
IROA Infrastructure Database Manager
Handles persistence of infrastructure inventory data
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class InfrastructureDBManager:
    """Manages database operations for infrastructure inventory"""
    
    def __init__(self, db_path: str = "data/iroa.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database with required schemas"""
        try:
            # Read and execute the inventory schemas
            schema_files = [
                "database/schemas.sql",
                "database/inventory_schemas.sql"
            ]
            
            with self.get_connection() as conn:
                for schema_file in schema_files:
                    if Path(schema_file).exists():
                        with open(schema_file, 'r') as f:
                            conn.executescript(f.read())
                        logger.info(f"Applied database schema: {schema_file}")
                    else:
                        logger.warning(f"Schema file not found: {schema_file}")
                
                conn.commit()
                logger.info("Database schemas initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_infrastructure_inventory(self, source: str, inventory: Dict[str, Any]) -> bool:
        """
        Save complete infrastructure inventory to database
        
        Args:
            source: Infrastructure source (vcenter, hyperv)
            inventory: Complete inventory data
            
        Returns:
            bool: Success status
        """
        try:
            sync_start = datetime.now()
            
            with self.get_connection() as conn:
                # Start sync history record
                sync_id = self._start_sync_history(conn, source, sync_start)
                
                records_processed = 0
                records_added = 0
                records_updated = 0
                
                # Save datacenters
                if 'datacenters' in inventory:
                    dc_stats = self._save_datacenters(conn, source, inventory['datacenters'])
                    records_processed += dc_stats['processed']
                    records_added += dc_stats['added']
                    records_updated += dc_stats['updated']
                
                # Save clusters  
                if 'clusters' in inventory:
                    cluster_stats = self._save_clusters(conn, source, inventory['clusters'])
                    records_processed += cluster_stats['processed']
                    records_added += cluster_stats['added']
                    records_updated += cluster_stats['updated']
                
                # Save hosts
                if 'hosts' in inventory:
                    host_stats = self._save_hosts(conn, source, inventory['hosts'])
                    records_processed += host_stats['processed']
                    records_added += host_stats['added']
                    records_updated += host_stats['updated']
                
                # Save datastores
                if 'datastores' in inventory:
                    ds_stats = self._save_datastores(conn, source, inventory['datastores'])
                    records_processed += ds_stats['processed']
                    records_added += ds_stats['added']
                    records_updated += ds_stats['updated']
                
                # Save networks
                if 'networks' in inventory:
                    net_stats = self._save_networks(conn, source, inventory['networks'])
                    records_processed += net_stats['processed']
                    records_added += net_stats['added']
                    records_updated += net_stats['updated']
                
                # Save VMs
                if 'vms' in inventory:
                    vm_stats = self._save_vms(conn, source, inventory['vms'])
                    records_processed += vm_stats['processed']
                    records_added += vm_stats['added']
                    records_updated += vm_stats['updated']
                
                # Complete sync history
                sync_end = datetime.now()
                duration = int((sync_end - sync_start).total_seconds())
                
                self._complete_sync_history(
                    conn, sync_id, sync_end, duration,
                    records_processed, records_added, records_updated, 0
                )
                
                # Update infrastructure summary
                self._update_infrastructure_summary(conn, source)
                
                conn.commit()
                
                logger.info(f"Successfully saved {source} inventory: "
                          f"{records_processed} processed, {records_added} added, {records_updated} updated")
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving {source} inventory: {e}")
            return False
    
    def _start_sync_history(self, conn: sqlite3.Connection, source: str, started_at: datetime) -> int:
        """Start sync history record"""
        cursor = conn.execute(
            "INSERT INTO infrastructure_sync_history (source, sync_type, status, started_at, triggered_by) "
            "VALUES (?, ?, ?, ?, ?)",
            (source, 'full', 'running', started_at, 'api')
        )
        return cursor.lastrowid
    
    def _complete_sync_history(self, conn: sqlite3.Connection, sync_id: int, completed_at: datetime,
                             duration: int, processed: int, added: int, updated: int, deleted: int):
        """Complete sync history record"""
        conn.execute(
            "UPDATE infrastructure_sync_history SET "
            "status = ?, completed_at = ?, duration_seconds = ?, "
            "records_processed = ?, records_added = ?, records_updated = ?, records_deleted = ? "
            "WHERE id = ?",
            ('success', completed_at, duration, processed, added, updated, deleted, sync_id)
        )
    
    def _save_datacenters(self, conn: sqlite3.Connection, source: str, datacenters: List[Dict]) -> Dict[str, int]:
        """Save datacenters to database"""
        stats = {'processed': 0, 'added': 0, 'updated': 0}
        
        for dc in datacenters:
            stats['processed'] += 1
            
            # Check if datacenter exists
            existing = conn.execute(
                "SELECT id FROM infrastructure_datacenters WHERE name = ? AND source = ?",
                (dc['name'], source)
            ).fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE infrastructure_datacenters SET "
                    "moid = ?, description = ?, updated_at = ?, last_sync = ? "
                    "WHERE id = ?",
                    (dc.get('moid'), dc.get('description'), now, now, existing['id'])
                )
                stats['updated'] += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO infrastructure_datacenters "
                    "(name, moid, source, description, last_sync) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (dc['name'], dc.get('moid'), source, dc.get('description'), now)
                )
                stats['added'] += 1
        
        return stats
    
    def _save_clusters(self, conn: sqlite3.Connection, source: str, clusters: List[Dict]) -> Dict[str, int]:
        """Save clusters to database"""
        stats = {'processed': 0, 'added': 0, 'updated': 0}
        
        for cluster in clusters:
            stats['processed'] += 1
            
            # Get datacenter ID
            datacenter_id = None
            if cluster.get('datacenter'):
                dc_row = conn.execute(
                    "SELECT id FROM infrastructure_datacenters WHERE name = ? AND source = ?",
                    (cluster['datacenter'], source)
                ).fetchone()
                if dc_row:
                    datacenter_id = dc_row['id']
            
            # Check if cluster exists
            existing = conn.execute(
                "SELECT id FROM infrastructure_clusters WHERE name = ? AND source = ?",
                (cluster['name'], source)
            ).fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE infrastructure_clusters SET "
                    "moid = ?, datacenter_id = ?, total_cpu_cores = ?, total_cpu_mhz = ?, "
                    "used_cpu_mhz = ?, total_memory_gb = ?, used_memory_gb = ?, "
                    "num_hosts = ?, num_vms = ?, drs_enabled = ?, ha_enabled = ?, "
                    "updated_at = ?, last_sync = ? "
                    "WHERE id = ?",
                    (
                        cluster.get('moid'), datacenter_id, cluster.get('total_cpu_cores', 0),
                        cluster.get('total_cpu_mhz', 0), cluster.get('used_cpu_mhz', 0),
                        cluster.get('total_memory_gb', 0), cluster.get('used_memory_gb', 0),
                        cluster.get('num_hosts', 0), cluster.get('num_vms', 0),
                        cluster.get('drs_enabled', False), cluster.get('ha_enabled', False),
                        now, now, existing['id']
                    )
                )
                stats['updated'] += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO infrastructure_clusters "
                    "(name, moid, datacenter_id, source, total_cpu_cores, total_cpu_mhz, "
                    "used_cpu_mhz, total_memory_gb, used_memory_gb, num_hosts, num_vms, "
                    "drs_enabled, ha_enabled, last_sync) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        cluster['name'], cluster.get('moid'), datacenter_id, source,
                        cluster.get('total_cpu_cores', 0), cluster.get('total_cpu_mhz', 0),
                        cluster.get('used_cpu_mhz', 0), cluster.get('total_memory_gb', 0),
                        cluster.get('used_memory_gb', 0), cluster.get('num_hosts', 0),
                        cluster.get('num_vms', 0), cluster.get('drs_enabled', False),
                        cluster.get('ha_enabled', False), now
                    )
                )
                stats['added'] += 1
        
        return stats
    
    def _save_hosts(self, conn: sqlite3.Connection, source: str, hosts: List[Dict]) -> Dict[str, int]:
        """Save hosts to database"""
        stats = {'processed': 0, 'added': 0, 'updated': 0}
        
        for host in hosts:
            stats['processed'] += 1
            
            # Get cluster and datacenter IDs
            cluster_id = None
            datacenter_id = None
            
            if host.get('cluster'):
                cluster_row = conn.execute(
                    "SELECT id, datacenter_id FROM infrastructure_clusters WHERE name = ? AND source = ?",
                    (host['cluster'], source)
                ).fetchone()
                if cluster_row:
                    cluster_id = cluster_row['id']
                    datacenter_id = cluster_row['datacenter_id']
            
            # Check if host exists
            existing = conn.execute(
                "SELECT id FROM infrastructure_hosts WHERE name = ? AND source = ?",
                (host['name'], source)
            ).fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE infrastructure_hosts SET "
                    "moid = ?, cluster_id = ?, datacenter_id = ?, cpu_cores = ?, "
                    "logical_cores = ?, cpu_threads = ?, cpu_mhz = ?, memory_gb = ?, "
                    "cpu_usage_mhz = ?, memory_usage_gb = ?, power_state = ?, "
                    "connection_state = ?, num_vms = ?, vendor = ?, model = ?, version = ?, "
                    "updated_at = ?, last_sync = ? "
                    "WHERE id = ?",
                    (
                        host.get('moid'), cluster_id, datacenter_id, host.get('cpu_cores', 0),
                        host.get('logical_cores', 0), host.get('cpu_threads', 0),
                        host.get('cpu_mhz', 0), host.get('memory_gb', 0),
                        host.get('cpu_usage_mhz', 0), host.get('memory_usage_gb', 0),
                        host.get('power_state', 'unknown'), host.get('connection_state', 'unknown'),
                        host.get('num_vms', 0), host.get('vendor'), host.get('model'),
                        host.get('version'), now, now, existing['id']
                    )
                )
                stats['updated'] += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO infrastructure_hosts "
                    "(name, moid, cluster_id, datacenter_id, source, cpu_cores, logical_cores, "
                    "cpu_threads, cpu_mhz, memory_gb, cpu_usage_mhz, memory_usage_gb, "
                    "power_state, connection_state, num_vms, vendor, model, version, last_sync) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        host['name'], host.get('moid'), cluster_id, datacenter_id, source,
                        host.get('cpu_cores', 0), host.get('logical_cores', 0),
                        host.get('cpu_threads', 0), host.get('cpu_mhz', 0),
                        host.get('memory_gb', 0), host.get('cpu_usage_mhz', 0),
                        host.get('memory_usage_gb', 0), host.get('power_state', 'unknown'),
                        host.get('connection_state', 'unknown'), host.get('num_vms', 0),
                        host.get('vendor'), host.get('model'), host.get('version'), now
                    )
                )
                stats['added'] += 1
        
        return stats
    
    def _save_datastores(self, conn: sqlite3.Connection, source: str, datastores: List[Dict]) -> Dict[str, int]:
        """Save datastores to database"""
        stats = {'processed': 0, 'added': 0, 'updated': 0}
        
        for ds in datastores:
            stats['processed'] += 1
            
            # Handle different datastore formats (vCenter vs HyperV)
            name = ds.get('name') or f"{ds.get('DriveLetter', 'Unknown')}:"
            
            # Check if datastore exists
            existing = conn.execute(
                "SELECT id FROM infrastructure_datastores WHERE name = ? AND source = ?",
                (name, source)
            ).fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE infrastructure_datastores SET "
                    "moid = ?, type = ?, capacity_gb = ?, free_space_gb = ?, "
                    "used_space_gb = ?, usage_percent = ?, accessible = ?, "
                    "maintenance_mode = ?, num_vms = ?, drive_letter = ?, "
                    "file_system = ?, label = ?, updated_at = ?, last_sync = ? "
                    "WHERE id = ?",
                    (
                        ds.get('moid'), ds.get('type') or ds.get('FileSystem'),
                        ds.get('capacity_gb') or ds.get('SizeGB', 0),
                        ds.get('free_space_gb') or ds.get('FreeSpaceGB', 0),
                        ds.get('used_space_gb') or ds.get('UsedSpaceGB', 0),
                        ds.get('usage_percent') or ds.get('UsagePercent', 0),
                        ds.get('accessible', True), ds.get('maintenance_mode', 'normal'),
                        ds.get('num_vms', 0), ds.get('DriveLetter'),
                        ds.get('FileSystem'), ds.get('Label'), now, now, existing['id']
                    )
                )
                stats['updated'] += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO infrastructure_datastores "
                    "(name, moid, source, type, capacity_gb, free_space_gb, used_space_gb, "
                    "usage_percent, accessible, maintenance_mode, num_vms, drive_letter, "
                    "file_system, label, last_sync) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        name, ds.get('moid'), source, ds.get('type') or ds.get('FileSystem'),
                        ds.get('capacity_gb') or ds.get('SizeGB', 0),
                        ds.get('free_space_gb') or ds.get('FreeSpaceGB', 0),
                        ds.get('used_space_gb') or ds.get('UsedSpaceGB', 0),
                        ds.get('usage_percent') or ds.get('UsagePercent', 0),
                        ds.get('accessible', True), ds.get('maintenance_mode', 'normal'),
                        ds.get('num_vms', 0), ds.get('DriveLetter'),
                        ds.get('FileSystem'), ds.get('Label'), now
                    )
                )
                stats['added'] += 1
        
        return stats
    
    def _save_networks(self, conn: sqlite3.Connection, source: str, networks: List[Dict]) -> Dict[str, int]:
        """Save networks to database"""
        stats = {'processed': 0, 'added': 0, 'updated': 0}
        
        for net in networks:
            stats['processed'] += 1
            
            # Check if network exists
            existing = conn.execute(
                "SELECT id FROM infrastructure_networks WHERE name = ? AND source = ?",
                (net['name'], source)
            ).fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE infrastructure_networks SET "
                    "moid = ?, network_type = ?, accessible = ?, num_vms = ?, "
                    "switch_type = ?, adapter_description = ?, allow_management_os = ?, "
                    "updated_at = ?, last_sync = ? "
                    "WHERE id = ?",
                    (
                        net.get('moid'), net.get('SwitchType'), net.get('accessible', True),
                        net.get('num_vms', 0), net.get('SwitchType'),
                        net.get('NetAdapterInterfaceDescription'), net.get('AllowManagementOS', False),
                        now, now, existing['id']
                    )
                )
                stats['updated'] += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO infrastructure_networks "
                    "(name, moid, source, network_type, accessible, num_vms, switch_type, "
                    "adapter_description, allow_management_os, last_sync) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        net['name'], net.get('moid'), source, net.get('SwitchType'),
                        net.get('accessible', True), net.get('num_vms', 0),
                        net.get('SwitchType'), net.get('NetAdapterInterfaceDescription'),
                        net.get('AllowManagementOS', False), now
                    )
                )
                stats['added'] += 1
        
        return stats
    
    def _save_vms(self, conn: sqlite3.Connection, source: str, vms: List[Dict]) -> Dict[str, int]:
        """Save VMs to database"""
        stats = {'processed': 0, 'added': 0, 'updated': 0}
        
        for vm in vms:
            stats['processed'] += 1
            
            # Get related IDs
            cluster_id = self._get_cluster_id(conn, vm.get('cluster'), source)
            host_id = self._get_host_id(conn, vm.get('host'), source)
            datacenter_id = self._get_datacenter_id(conn, vm.get('datacenter'), source)
            
            # Handle different VM name formats
            vm_name = vm.get('vm') or vm.get('name')
            
            # Check if VM exists
            existing = conn.execute(
                "SELECT id FROM infrastructure_vms WHERE name = ? AND source = ?",
                (vm_name, source)
            ).fetchone()
            
            now = datetime.now()
            
            if existing:
                # Update existing
                conn.execute(
                    "UPDATE infrastructure_vms SET "
                    "moid = ?, vm_id = ?, cluster_id = ?, host_id = ?, datacenter_id = ?, "
                    "status = ?, power_state = ?, cpu_cores = ?, memory_gb = ?, "
                    "cpu_usage_percent = ?, memory_usage_percent = ?, guest_os = ?, "
                    "tools_status = ?, annotation = ?, updated_at = ?, last_sync = ? "
                    "WHERE id = ?",
                    (
                        vm.get('moid'), vm.get('uuid') or vm.get('vm_id'), cluster_id, host_id,
                        datacenter_id, vm.get('status', 'unknown'), vm.get('power_state', 'unknown'),
                        vm.get('cores', 1), vm.get('memory', 1), vm.get('cpu', 0),
                        vm.get('memory_usage', 0), vm.get('guest_os'), vm.get('tools_status'),
                        vm.get('details', {}).get('annotation'), now, now, existing['id']
                    )
                )
                stats['updated'] += 1
            else:
                # Insert new
                conn.execute(
                    "INSERT INTO infrastructure_vms "
                    "(name, moid, vm_id, cluster_id, host_id, datacenter_id, source, status, "
                    "power_state, cpu_cores, memory_gb, cpu_usage_percent, memory_usage_percent, "
                    "guest_os, tools_status, annotation, last_sync) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        vm_name, vm.get('moid'), vm.get('uuid') or vm.get('vm_id'),
                        cluster_id, host_id, datacenter_id, source, vm.get('status', 'unknown'),
                        vm.get('power_state', 'unknown'), vm.get('cores', 1), vm.get('memory', 1),
                        vm.get('cpu', 0), vm.get('memory_usage', 0), vm.get('guest_os'),
                        vm.get('tools_status'), vm.get('details', {}).get('annotation'), now
                    )
                )
                stats['added'] += 1
        
        return stats
    
    def _get_cluster_id(self, conn: sqlite3.Connection, cluster_name: str, source: str) -> Optional[int]:
        """Get cluster ID by name"""
        if not cluster_name:
            return None
        
        row = conn.execute(
            "SELECT id FROM infrastructure_clusters WHERE name = ? AND source = ?",
            (cluster_name, source)
        ).fetchone()
        
        return row['id'] if row else None
    
    def _get_host_id(self, conn: sqlite3.Connection, host_name: str, source: str) -> Optional[int]:
        """Get host ID by name"""
        if not host_name:
            return None
            
        row = conn.execute(
            "SELECT id FROM infrastructure_hosts WHERE name = ? AND source = ?",
            (host_name, source)
        ).fetchone()
        
        return row['id'] if row else None
    
    def _get_datacenter_id(self, conn: sqlite3.Connection, datacenter_name: str, source: str) -> Optional[int]:
        """Get datacenter ID by name"""
        if not datacenter_name:
            return None
            
        row = conn.execute(
            "SELECT id FROM infrastructure_datacenters WHERE name = ? AND source = ?",
            (datacenter_name, source)
        ).fetchone()
        
        return row['id'] if row else None
    
    def _update_infrastructure_summary(self, conn: sqlite3.Connection, source: str):
        """Update infrastructure summary statistics"""
        try:
            # Calculate summary statistics
            summary_query = """
                SELECT 
                    COUNT(DISTINCT d.id) as total_datacenters,
                    COUNT(DISTINCT c.id) as total_clusters,
                    COUNT(DISTINCT h.id) as total_hosts,
                    COUNT(DISTINCT ds.id) as total_datastores,
                    COUNT(DISTINCT n.id) as total_networks,
                    COUNT(DISTINCT v.id) as total_vms,
                    SUM(CASE WHEN v.status = 'running' THEN 1 ELSE 0 END) as running_vms,
                    SUM(CASE WHEN v.status = 'stopped' THEN 1 ELSE 0 END) as stopped_vms,
                    SUM(COALESCE(h.cpu_cores, 0)) as total_cpu_cores,
                    SUM(COALESCE(h.memory_gb, 0)) as total_memory_gb,
                    SUM(COALESCE(ds.capacity_gb, 0)) as total_storage_gb,
                    SUM(COALESCE(ds.used_space_gb, 0)) as used_storage_gb,
                    AVG(COALESCE(v.cpu_usage_percent, 0)) as avg_cpu_utilization,
                    AVG(COALESCE(v.memory_usage_percent, 0)) as avg_memory_utilization,
                    SUM(CASE WHEN v.status = 'running' AND v.cpu_usage_percent < 30 AND v.memory_usage_percent < 50 THEN 1 ELSE 0 END) as underutilized_vms
                FROM (SELECT ? as source) src
                LEFT JOIN infrastructure_datacenters d ON d.source = src.source AND d.is_active = 1
                LEFT JOIN infrastructure_clusters c ON c.source = src.source AND c.is_active = 1
                LEFT JOIN infrastructure_hosts h ON h.source = src.source AND h.is_active = 1
                LEFT JOIN infrastructure_datastores ds ON ds.source = src.source AND ds.is_active = 1
                LEFT JOIN infrastructure_networks n ON n.source = src.source AND n.is_active = 1
                LEFT JOIN infrastructure_vms v ON v.source = src.source AND v.is_active = 1
            """
            
            result = conn.execute(summary_query, (source,)).fetchone()
            
            if result:
                # Insert or update summary
                conn.execute(
                    "INSERT OR REPLACE INTO infrastructure_summary "
                    "(source, total_datacenters, total_clusters, total_hosts, total_datastores, "
                    "total_networks, total_vms, running_vms, stopped_vms, total_cpu_cores, "
                    "total_memory_gb, total_storage_gb, used_storage_gb, avg_cpu_utilization, "
                    "avg_memory_utilization, underutilized_vms, last_updated) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        source, result['total_datacenters'], result['total_clusters'],
                        result['total_hosts'], result['total_datastores'], result['total_networks'],
                        result['total_vms'], result['running_vms'], result['stopped_vms'],
                        result['total_cpu_cores'], result['total_memory_gb'], result['total_storage_gb'],
                        result['used_storage_gb'], result['avg_cpu_utilization'],
                        result['avg_memory_utilization'], result['underutilized_vms'],
                        datetime.now()
                    )
                )
                
                logger.info(f"Updated infrastructure summary for {source}")
                
        except Exception as e:
            logger.error(f"Error updating infrastructure summary for {source}: {e}")
    
    def get_infrastructure_inventory(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete infrastructure inventory from database
        
        Args:
            source: Infrastructure source (vcenter, hyperv)
            
        Returns:
            Complete inventory data or None if not found
        """
        try:
            with self.get_connection() as conn:
                # Get summary
                summary = conn.execute(
                    "SELECT * FROM infrastructure_summary WHERE source = ?",
                    (source,)
                ).fetchone()
                
                if not summary:
                    return None
                
                # Get detailed data
                inventory = {
                    'datacenters': self._get_datacenters(conn, source),
                    'clusters': self._get_clusters(conn, source),
                    'hosts': self._get_hosts(conn, source),
                    'datastores': self._get_datastores(conn, source),
                    'networks': self._get_networks(conn, source),
                    'vms': self._get_vms(conn, source),
                    'summary': dict(summary)
                }
                
                return inventory
                
        except Exception as e:
            logger.error(f"Error retrieving {source} inventory: {e}")
            return None
    
    def _get_datacenters(self, conn: sqlite3.Connection, source: str) -> List[Dict]:
        """Get datacenters from database"""
        rows = conn.execute(
            "SELECT * FROM infrastructure_datacenters WHERE source = ? AND is_active = 1",
            (source,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def _get_clusters(self, conn: sqlite3.Connection, source: str) -> List[Dict]:
        """Get clusters from database"""
        rows = conn.execute(
            "SELECT c.*, d.name as datacenter_name "
            "FROM infrastructure_clusters c "
            "LEFT JOIN infrastructure_datacenters d ON c.datacenter_id = d.id "
            "WHERE c.source = ? AND c.is_active = 1",
            (source,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def _get_hosts(self, conn: sqlite3.Connection, source: str) -> List[Dict]:
        """Get hosts from database"""
        rows = conn.execute(
            "SELECT h.*, c.name as cluster_name, d.name as datacenter_name "
            "FROM infrastructure_hosts h "
            "LEFT JOIN infrastructure_clusters c ON h.cluster_id = c.id "
            "LEFT JOIN infrastructure_datacenters d ON h.datacenter_id = d.id "
            "WHERE h.source = ? AND h.is_active = 1",
            (source,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def _get_datastores(self, conn: sqlite3.Connection, source: str) -> List[Dict]:
        """Get datastores from database"""
        rows = conn.execute(
            "SELECT * FROM infrastructure_datastores WHERE source = ? AND is_active = 1",
            (source,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def _get_networks(self, conn: sqlite3.Connection, source: str) -> List[Dict]:
        """Get networks from database"""
        rows = conn.execute(
            "SELECT * FROM infrastructure_networks WHERE source = ? AND is_active = 1",
            (source,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def _get_vms(self, conn: sqlite3.Connection, source: str) -> List[Dict]:
        """Get VMs from database"""
        rows = conn.execute(
            "SELECT v.*, c.name as cluster_name, h.name as host_name, d.name as datacenter_name "
            "FROM infrastructure_vms v "
            "LEFT JOIN infrastructure_clusters c ON v.cluster_id = c.id "
            "LEFT JOIN infrastructure_hosts h ON v.host_id = h.id "
            "LEFT JOIN infrastructure_datacenters d ON v.datacenter_id = d.id "
            "WHERE v.source = ? AND v.is_active = 1",
            (source,)
        ).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_sync_history(self, source: str, limit: int = 10) -> List[Dict]:
        """Get sync history for a source"""
        try:
            with self.get_connection() as conn:
                rows = conn.execute(
                    "SELECT * FROM infrastructure_sync_history "
                    "WHERE source = ? ORDER BY started_at DESC LIMIT ?",
                    (source, limit)
                ).fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving sync history for {source}: {e}")
            return []