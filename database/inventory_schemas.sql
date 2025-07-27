-- IROA Infrastructure Inventory Database Schemas
-- Additional database schema for infrastructure inventory persistence

-- Infrastructure Datacenters Schema
CREATE TABLE IF NOT EXISTS infrastructure_datacenters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    moid VARCHAR(255) UNIQUE, -- Managed Object ID for vCenter
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    location VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP
);

-- Infrastructure Clusters Schema
CREATE TABLE IF NOT EXISTS infrastructure_clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    moid VARCHAR(255), -- Managed Object ID
    datacenter_id INTEGER,
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    total_cpu_cores INTEGER DEFAULT 0,
    total_cpu_mhz INTEGER DEFAULT 0,
    used_cpu_mhz INTEGER DEFAULT 0,
    total_memory_gb DECIMAL(10,2) DEFAULT 0.00,
    used_memory_gb DECIMAL(10,2) DEFAULT 0.00,
    num_hosts INTEGER DEFAULT 0,
    num_vms INTEGER DEFAULT 0,
    drs_enabled BOOLEAN DEFAULT FALSE,
    ha_enabled BOOLEAN DEFAULT FALSE,
    cpu_utilization_percent DECIMAL(5,2) DEFAULT 0.00,
    memory_utilization_percent DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    FOREIGN KEY (datacenter_id) REFERENCES infrastructure_datacenters(id)
);

-- Infrastructure Hosts Schema
CREATE TABLE IF NOT EXISTS infrastructure_hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    moid VARCHAR(255), -- Managed Object ID
    cluster_id INTEGER,
    datacenter_id INTEGER,
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    cpu_cores INTEGER DEFAULT 0,
    logical_cores INTEGER DEFAULT 0,
    cpu_threads INTEGER DEFAULT 0,
    cpu_mhz INTEGER DEFAULT 0,
    memory_gb DECIMAL(10,2) DEFAULT 0.00,
    cpu_usage_mhz INTEGER DEFAULT 0,
    memory_usage_gb DECIMAL(10,2) DEFAULT 0.00,
    power_state VARCHAR(20) DEFAULT 'poweredOn',
    connection_state VARCHAR(20) DEFAULT 'connected',
    num_vms INTEGER DEFAULT 0,
    vendor VARCHAR(100),
    model VARCHAR(255),
    version VARCHAR(100),
    ip_address VARCHAR(45),
    cpu_utilization_percent DECIMAL(5,2) DEFAULT 0.00,
    memory_utilization_percent DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES infrastructure_clusters(id),
    FOREIGN KEY (datacenter_id) REFERENCES infrastructure_datacenters(id)
);

-- Infrastructure Datastores Schema
CREATE TABLE IF NOT EXISTS infrastructure_datastores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    moid VARCHAR(255), -- Managed Object ID
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    type VARCHAR(50), -- VMFS, NFS, VSAN, NTFS, etc.
    capacity_gb DECIMAL(12,2) DEFAULT 0.00,
    free_space_gb DECIMAL(12,2) DEFAULT 0.00,
    used_space_gb DECIMAL(12,2) DEFAULT 0.00,
    usage_percent DECIMAL(5,2) DEFAULT 0.00,
    accessible BOOLEAN DEFAULT TRUE,
    maintenance_mode VARCHAR(20) DEFAULT 'normal',
    num_vms INTEGER DEFAULT 0,
    drive_letter VARCHAR(5), -- For HyperV volumes
    file_system VARCHAR(20),
    label VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP
);

-- Infrastructure Networks Schema
CREATE TABLE IF NOT EXISTS infrastructure_networks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    moid VARCHAR(255), -- Managed Object ID
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    network_type VARCHAR(50), -- Standard, Distributed, External, Internal, Private
    accessible BOOLEAN DEFAULT TRUE,
    num_vms INTEGER DEFAULT 0,
    vlan_id INTEGER,
    switch_type VARCHAR(50), -- For HyperV: External, Internal, Private
    adapter_description TEXT,
    allow_management_os BOOLEAN DEFAULT FALSE, -- HyperV specific
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP
);

-- Enhanced Infrastructure VMs Schema (replacing basic vm_metrics for inventory)
CREATE TABLE IF NOT EXISTS infrastructure_vms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    moid VARCHAR(255), -- Managed Object ID
    vm_id VARCHAR(255), -- UUID or unique identifier
    cluster_id INTEGER,
    host_id INTEGER,
    datacenter_id INTEGER,
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    status VARCHAR(20) DEFAULT 'unknown', -- running, stopped, suspended
    power_state VARCHAR(20) DEFAULT 'unknown',
    cpu_cores INTEGER DEFAULT 1,
    memory_gb DECIMAL(10,2) DEFAULT 1.00,
    cpu_usage_percent DECIMAL(5,2) DEFAULT 0.00,
    memory_usage_percent DECIMAL(5,2) DEFAULT 0.00,
    disk_usage_gb DECIMAL(10,2) DEFAULT 0.00,
    guest_os VARCHAR(255),
    tools_status VARCHAR(50),
    vm_generation INTEGER, -- HyperV Generation 1 or 2
    dynamic_memory_enabled BOOLEAN DEFAULT FALSE, -- HyperV specific
    memory_minimum_gb DECIMAL(10,2), -- HyperV dynamic memory
    memory_maximum_gb DECIMAL(10,2), -- HyperV dynamic memory
    network_adapters INTEGER DEFAULT 1,
    hard_disks INTEGER DEFAULT 1,
    vm_version VARCHAR(50),
    vm_path TEXT,
    creation_time TIMESTAMP,
    last_boot_time TIMESTAMP,
    annotation TEXT,
    is_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    FOREIGN KEY (cluster_id) REFERENCES infrastructure_clusters(id),
    FOREIGN KEY (host_id) REFERENCES infrastructure_hosts(id),
    FOREIGN KEY (datacenter_id) REFERENCES infrastructure_datacenters(id)
);

-- VM to Datastore mapping (many-to-many)
CREATE TABLE IF NOT EXISTS vm_datastore_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id INTEGER NOT NULL,
    datastore_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vm_id) REFERENCES infrastructure_vms(id),
    FOREIGN KEY (datastore_id) REFERENCES infrastructure_datastores(id),
    UNIQUE(vm_id, datastore_id)
);

-- VM to Network mapping (many-to-many)
CREATE TABLE IF NOT EXISTS vm_network_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id INTEGER NOT NULL,
    network_id INTEGER NOT NULL,
    adapter_type VARCHAR(50),
    mac_address VARCHAR(17),
    ip_address VARCHAR(45),
    connected BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vm_id) REFERENCES infrastructure_vms(id),
    FOREIGN KEY (network_id) REFERENCES infrastructure_networks(id)
);

-- Infrastructure Sync History
CREATE TABLE IF NOT EXISTS infrastructure_sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(50) NOT NULL, -- vcenter, hyperv, etc.
    sync_type VARCHAR(50) NOT NULL, -- full, incremental
    status VARCHAR(20) NOT NULL, -- success, failed, partial
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    records_processed INTEGER DEFAULT 0,
    records_added INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    error_message TEXT,
    sync_details TEXT, -- JSON with detailed sync information
    triggered_by VARCHAR(100) DEFAULT 'manual' -- manual, scheduled, api
);

-- Infrastructure Summary View (materialized view simulation)
CREATE TABLE IF NOT EXISTS infrastructure_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(50) NOT NULL,
    total_datacenters INTEGER DEFAULT 0,
    total_clusters INTEGER DEFAULT 0,
    total_hosts INTEGER DEFAULT 0,
    total_datastores INTEGER DEFAULT 0,
    total_networks INTEGER DEFAULT 0,
    total_vms INTEGER DEFAULT 0,
    running_vms INTEGER DEFAULT 0,
    stopped_vms INTEGER DEFAULT 0,
    total_cpu_cores INTEGER DEFAULT 0,
    total_memory_gb DECIMAL(12,2) DEFAULT 0.00,
    total_storage_gb DECIMAL(15,2) DEFAULT 0.00,
    used_storage_gb DECIMAL(15,2) DEFAULT 0.00,
    avg_cpu_utilization DECIMAL(5,2) DEFAULT 0.00,
    avg_memory_utilization DECIMAL(5,2) DEFAULT 0.00,
    underutilized_vms INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_infrastructure_vms_source ON infrastructure_vms(source);
CREATE INDEX IF NOT EXISTS idx_infrastructure_vms_status ON infrastructure_vms(status);
CREATE INDEX IF NOT EXISTS idx_infrastructure_vms_cluster ON infrastructure_vms(cluster_id);
CREATE INDEX IF NOT EXISTS idx_infrastructure_vms_host ON infrastructure_vms(host_id);
CREATE INDEX IF NOT EXISTS idx_infrastructure_vms_name ON infrastructure_vms(name);
CREATE INDEX IF NOT EXISTS idx_infrastructure_vms_last_sync ON infrastructure_vms(last_sync);

CREATE INDEX IF NOT EXISTS idx_infrastructure_clusters_source ON infrastructure_clusters(source);
CREATE INDEX IF NOT EXISTS idx_infrastructure_clusters_datacenter ON infrastructure_clusters(datacenter_id);
CREATE INDEX IF NOT EXISTS idx_infrastructure_clusters_last_sync ON infrastructure_clusters(last_sync);

CREATE INDEX IF NOT EXISTS idx_infrastructure_hosts_source ON infrastructure_hosts(source);
CREATE INDEX IF NOT EXISTS idx_infrastructure_hosts_cluster ON infrastructure_hosts(cluster_id);
CREATE INDEX IF NOT EXISTS idx_infrastructure_hosts_last_sync ON infrastructure_hosts(last_sync);

CREATE INDEX IF NOT EXISTS idx_infrastructure_datastores_source ON infrastructure_datastores(source);
CREATE INDEX IF NOT EXISTS idx_infrastructure_datastores_last_sync ON infrastructure_datastores(last_sync);

CREATE INDEX IF NOT EXISTS idx_infrastructure_networks_source ON infrastructure_networks(source);
CREATE INDEX IF NOT EXISTS idx_infrastructure_networks_last_sync ON infrastructure_networks(last_sync);

CREATE INDEX IF NOT EXISTS idx_infrastructure_sync_history_source ON infrastructure_sync_history(source);
CREATE INDEX IF NOT EXISTS idx_infrastructure_sync_history_started ON infrastructure_sync_history(started_at);

-- Triggers to update summary statistics
CREATE TRIGGER IF NOT EXISTS update_infrastructure_summary_after_vm_insert
AFTER INSERT ON infrastructure_vms
BEGIN
    INSERT OR REPLACE INTO infrastructure_summary (
        source, total_vms, running_vms, stopped_vms, last_updated
    )
    SELECT 
        NEW.source,
        COUNT(*) as total_vms,
        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_vms,
        SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) as stopped_vms,
        CURRENT_TIMESTAMP
    FROM infrastructure_vms 
    WHERE source = NEW.source AND is_active = TRUE;
END;

CREATE TRIGGER IF NOT EXISTS update_infrastructure_summary_after_vm_update
AFTER UPDATE ON infrastructure_vms
BEGIN
    INSERT OR REPLACE INTO infrastructure_summary (
        source, total_vms, running_vms, stopped_vms, last_updated
    )
    SELECT 
        NEW.source,
        COUNT(*) as total_vms,
        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_vms,
        SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) as stopped_vms,
        CURRENT_TIMESTAMP
    FROM infrastructure_vms 
    WHERE source = NEW.source AND is_active = TRUE;
END;