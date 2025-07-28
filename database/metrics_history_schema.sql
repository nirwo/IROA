-- Historical Metrics Storage for Forecasting Analysis
-- This schema stores time-series data for VMs, hosts, and clusters

-- VM Historical Metrics
CREATE TABLE IF NOT EXISTS vm_metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_id TEXT NOT NULL,
    vm_name TEXT NOT NULL,
    cluster_name TEXT NOT NULL,
    host_name TEXT,
    datacenter_name TEXT,
    
    -- Resource Allocation
    allocated_vcpus INTEGER NOT NULL DEFAULT 0,
    allocated_memory_gb REAL NOT NULL DEFAULT 0,
    allocated_storage_gb REAL NOT NULL DEFAULT 0,
    
    -- Actual Usage Metrics
    cpu_usage_percent REAL NOT NULL DEFAULT 0,  -- Actual CPU utilization %
    memory_usage_percent REAL NOT NULL DEFAULT 0,  -- Memory utilization %
    storage_usage_gb REAL NOT NULL DEFAULT 0,  -- Storage used in GB
    network_rx_mbps REAL DEFAULT 0,  -- Network receive Mbps
    network_tx_mbps REAL DEFAULT 0,  -- Network transmit Mbps
    
    -- Calculated Fields
    actual_cpu_cores_used REAL GENERATED ALWAYS AS (allocated_vcpus * (cpu_usage_percent / 100.0)) STORED,
    actual_memory_gb_used REAL GENERATED ALWAYS AS (allocated_memory_gb * (memory_usage_percent / 100.0)) STORED,
    
    -- Status and Power State
    power_state TEXT DEFAULT 'unknown',  -- poweredOn, poweredOff, suspended
    vm_status TEXT DEFAULT 'unknown',    -- running, stopped, error
    
    -- Timestamps
    metric_timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for time-series queries
    INDEX idx_vm_metrics_vm_time (vm_id, metric_timestamp),
    INDEX idx_vm_metrics_cluster_time (cluster_name, metric_timestamp),
    INDEX idx_vm_metrics_timestamp (metric_timestamp)
);

-- Host Historical Metrics  
CREATE TABLE IF NOT EXISTS host_metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_id TEXT NOT NULL,
    host_name TEXT NOT NULL,
    cluster_name TEXT NOT NULL,
    datacenter_name TEXT,
    
    -- Physical Resources
    physical_cpu_cores INTEGER NOT NULL DEFAULT 0,
    physical_memory_gb REAL NOT NULL DEFAULT 0,
    physical_storage_gb REAL NOT NULL DEFAULT 0,
    
    -- vCPU Overcommit
    total_vcpu_capacity INTEGER GENERATED ALWAYS AS (physical_cpu_cores * 4) STORED,  -- 4:1 ratio
    allocated_vcpus INTEGER NOT NULL DEFAULT 0,
    vcpu_allocation_percent REAL GENERATED ALWAYS AS (
        CASE WHEN total_vcpu_capacity > 0 
        THEN (allocated_vcpus * 100.0 / total_vcpu_capacity) 
        ELSE 0 END
    ) STORED,
    
    -- Actual Usage
    cpu_usage_percent REAL NOT NULL DEFAULT 0,  -- Physical CPU usage
    memory_usage_percent REAL NOT NULL DEFAULT 0,
    storage_usage_percent REAL NOT NULL DEFAULT 0,
    
    -- VM Counts
    total_vms INTEGER NOT NULL DEFAULT 0,
    running_vms INTEGER NOT NULL DEFAULT 0,
    
    -- Network and Storage I/O
    network_rx_mbps REAL DEFAULT 0,
    network_tx_mbps REAL DEFAULT 0,
    storage_read_iops REAL DEFAULT 0,
    storage_write_iops REAL DEFAULT 0,
    
    -- Status
    host_status TEXT DEFAULT 'unknown',  -- connected, disconnected, maintenance
    
    -- Timestamps
    metric_timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_host_metrics_host_time (host_id, metric_timestamp),
    INDEX idx_host_metrics_cluster_time (cluster_name, metric_timestamp),
    INDEX idx_host_metrics_timestamp (metric_timestamp)
);

-- Cluster Historical Metrics (Aggregated)
CREATE TABLE IF NOT EXISTS cluster_metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_name TEXT NOT NULL,
    datacenter_name TEXT,
    
    -- Physical Resources (sum of all hosts)
    total_physical_cpu_cores INTEGER NOT NULL DEFAULT 0,
    total_physical_memory_gb REAL NOT NULL DEFAULT 0,
    total_physical_storage_gb REAL NOT NULL DEFAULT 0,
    
    -- vCPU Overcommit
    total_vcpu_capacity INTEGER GENERATED ALWAYS AS (total_physical_cpu_cores * 4) STORED,
    total_allocated_vcpus INTEGER NOT NULL DEFAULT 0,
    vcpu_allocation_percent REAL GENERATED ALWAYS AS (
        CASE WHEN total_vcpu_capacity > 0 
        THEN (total_allocated_vcpus * 100.0 / total_vcpu_capacity) 
        ELSE 0 END
    ) STORED,
    
    -- Actual Usage (weighted average across hosts)
    avg_cpu_usage_percent REAL NOT NULL DEFAULT 0,
    avg_memory_usage_percent REAL NOT NULL DEFAULT 0,
    avg_storage_usage_percent REAL NOT NULL DEFAULT 0,
    
    -- VM and Host Counts
    total_hosts INTEGER NOT NULL DEFAULT 0,
    connected_hosts INTEGER NOT NULL DEFAULT 0,
    total_vms INTEGER NOT NULL DEFAULT 0,
    running_vms INTEGER NOT NULL DEFAULT 0,
    
    -- Peak Usage (for capacity planning)
    peak_cpu_usage_percent REAL DEFAULT 0,
    peak_memory_usage_percent REAL DEFAULT 0,
    peak_vcpu_allocation_percent REAL DEFAULT 0,
    
    -- Capacity Planning
    max_additional_vms_cpu INTEGER GENERATED ALWAYS AS (
        CASE WHEN total_vcpu_capacity > total_allocated_vcpus AND total_allocated_vcpus > 0
        THEN ((total_vcpu_capacity - total_allocated_vcpus) / (total_allocated_vcpus / total_vms))
        ELSE 0 END
    ) STORED,
    
    -- Timestamps
    metric_timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_cluster_metrics_cluster_time (cluster_name, metric_timestamp),
    INDEX idx_cluster_metrics_timestamp (metric_timestamp)
);

-- Forecasting Aggregates (Pre-calculated for performance)
CREATE TABLE IF NOT EXISTS forecasting_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type TEXT NOT NULL,  -- 'vm', 'host', 'cluster'
    resource_id TEXT NOT NULL,    -- vm_id, host_id, cluster_name
    metric_name TEXT NOT NULL,    -- 'cpu_usage', 'memory_usage', 'vcpu_allocation'
    
    -- Time period aggregates
    hourly_avg REAL,
    daily_avg REAL,
    weekly_avg REAL,
    monthly_avg REAL,
    
    -- Trend analysis
    growth_rate_daily REAL,      -- % change per day
    growth_rate_weekly REAL,     -- % change per week
    growth_rate_monthly REAL,    -- % change per month
    
    -- Statistical measures
    std_deviation REAL,
    min_value REAL,
    max_value REAL,
    percentile_95 REAL,
    
    -- Forecast predictions (next 30 days)
    forecast_7d REAL,
    forecast_14d REAL,
    forecast_30d REAL,
    forecast_confidence REAL,    -- 0-100% confidence
    
    -- Time range this aggregate covers
    period_start DATETIME NOT NULL,
    period_end DATETIME NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_forecasting_resource (resource_type, resource_id),
    INDEX idx_forecasting_metric (metric_name),
    INDEX idx_forecasting_period (period_start, period_end)
);

-- Events and Anomalies
CREATE TABLE IF NOT EXISTS infrastructure_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,     -- 'vm_created', 'vm_deleted', 'host_maintenance', 'resource_alert'
    severity TEXT NOT NULL,       -- 'info', 'warning', 'critical'
    resource_type TEXT NOT NULL,  -- 'vm', 'host', 'cluster'
    resource_id TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    
    -- Event details
    title TEXT NOT NULL,
    description TEXT,
    metric_name TEXT,             -- If related to a specific metric
    threshold_value REAL,         -- Alert threshold that was crossed
    actual_value REAL,            -- Actual value that triggered the event
    
    -- Resolution
    status TEXT DEFAULT 'open',   -- 'open', 'acknowledged', 'resolved'
    resolved_at DATETIME,
    resolved_by TEXT,
    
    -- Timestamps
    event_timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_events_resource (resource_type, resource_id),
    INDEX idx_events_timestamp (event_timestamp),
    INDEX idx_events_status (status),
    INDEX idx_events_severity (severity)
);

-- Cleanup old metrics (keep last 90 days for detailed, 1 year for aggregates)
-- This should be run as a scheduled job
CREATE TRIGGER IF NOT EXISTS cleanup_old_vm_metrics 
AFTER INSERT ON vm_metrics_history
WHEN NEW.id % 1000 = 0  -- Run cleanup every 1000 inserts
BEGIN
    DELETE FROM vm_metrics_history 
    WHERE metric_timestamp < datetime('now', '-90 days');
END;

CREATE TRIGGER IF NOT EXISTS cleanup_old_host_metrics 
AFTER INSERT ON host_metrics_history
WHEN NEW.id % 1000 = 0
BEGIN
    DELETE FROM host_metrics_history 
    WHERE metric_timestamp < datetime('now', '-90 days');
END;

CREATE TRIGGER IF NOT EXISTS cleanup_old_cluster_metrics 
AFTER INSERT ON cluster_metrics_history
WHEN NEW.id % 500 = 0
BEGIN
    DELETE FROM cluster_metrics_history 
    WHERE metric_timestamp < datetime('now', '-365 days');
END;