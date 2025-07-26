-- IROA Database Schemas
-- Complete database schema for all IROA components

-- License Management Schema
CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'Perpetual', -- Perpetual, Subscription, Trial
    total INTEGER NOT NULL DEFAULT 1,
    used INTEGER NOT NULL DEFAULT 0,
    cost DECIMAL(10,2) DEFAULT 0.00,
    expiry_date DATE,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, expiring, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Capacity Planning Schema
CREATE TABLE IF NOT EXISTS capacity_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_cpu_cores INTEGER NOT NULL,
    total_memory_gb DECIMAL(10,2) NOT NULL,
    used_cpu_cores INTEGER NOT NULL,
    used_memory_gb DECIMAL(10,2) NOT NULL,
    cpu_utilization_percent DECIMAL(5,2) NOT NULL,
    memory_utilization_percent DECIMAL(5,2) NOT NULL,
    max_additional_vms INTEGER NOT NULL,
    recommendations TEXT,
    limiting_factor VARCHAR(50) -- CPU, Memory, Storage, License
);

-- VM Profile Templates Schema
CREATE TABLE IF NOT EXISTS vm_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cpu_cores INTEGER NOT NULL,
    memory_gb DECIMAL(5,2) NOT NULL,
    storage_gb INTEGER DEFAULT 50,
    estimated_cost DECIMAL(10,2) DEFAULT 0.00,
    license_requirements TEXT, -- JSON array of required licenses
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Administration Configuration Schema
CREATE TABLE IF NOT EXISTS admin_configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integration_type VARCHAR(50) NOT NULL, -- vcenter, zabbix, prometheus, mac
    config_name VARCHAR(255) NOT NULL,
    host VARCHAR(255),
    port INTEGER,
    username VARCHAR(255),
    password_encrypted TEXT, -- Encrypted password storage
    url TEXT,
    additional_config TEXT, -- JSON for extra configuration
    is_active BOOLEAN DEFAULT TRUE,
    last_tested TIMESTAMP,
    test_status VARCHAR(20) DEFAULT 'unknown', -- success, failed, unknown
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VM Metrics Schema (Enhanced)
CREATE TABLE IF NOT EXISTS vm_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vm_name VARCHAR(255) NOT NULL,
    hostname VARCHAR(255),
    cluster VARCHAR(255),
    datacenter VARCHAR(255),
    cpu_cores INTEGER,
    memory_gb DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_percent DECIMAL(5,2),
    disk_usage_percent DECIMAL(5,2),
    network_usage_mbps DECIMAL(10,2),
    disk_io_iops INTEGER,
    net_io_mbps DECIMAL(10,2),
    power_state VARCHAR(20) DEFAULT 'poweredOn',
    guest_os VARCHAR(255),
    vm_tools_status VARCHAR(50),
    uptime_hours INTEGER,
    snapshot_count INTEGER DEFAULT 0,
    is_template BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'vcenter', -- vcenter, prometheus, manual
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations Schema
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(50) NOT NULL, -- optimization, memory, capacity, cost
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    impact TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, dismissed, implemented
    vm_id INTEGER, -- Reference to specific VM if applicable
    estimated_savings DECIMAL(10,2) DEFAULT 0.00,
    implementation_effort VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    category VARCHAR(50), -- performance, cost, security, compliance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vm_id) REFERENCES vm_metrics(id)
);

-- Analytics Data Schema
CREATE TABLE IF NOT EXISTS analytics_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit VARCHAR(20),
    source VARCHAR(50) NOT NULL, -- prometheus, vcenter, system
    tags TEXT, -- JSON for additional metadata
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Health Schema
CREATE TABLE IF NOT EXISTS system_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component VARCHAR(50) NOT NULL, -- api, database, prometheus, vcenter
    status VARCHAR(20) NOT NULL, -- healthy, degraded, down
    response_time_ms INTEGER,
    error_message TEXT,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uptime_percent DECIMAL(5,2) DEFAULT 100.00
);

-- Audit Log Schema
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(100) DEFAULT 'system',
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50), -- license, vm, configuration
    resource_id INTEGER,
    old_values TEXT, -- JSON
    new_values TEXT, -- JSON
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default VM profiles
INSERT OR IGNORE INTO vm_profiles (name, description, cpu_cores, memory_gb, storage_gb, license_requirements) VALUES
('Small Development', 'Basic development environment', 2, 4.0, 50, '["Windows Server", "Visual Studio"]'),
('Medium Production', 'Standard production workload', 4, 8.0, 100, '["Windows Server", "SQL Server"]'),
('Large Database', 'High-performance database server', 8, 16.0, 500, '["Windows Server", "SQL Server Enterprise"]'),
('Micro Service', 'Lightweight microservice container', 1, 2.0, 20, '["Linux"]'),
('Enterprise Application', 'Large enterprise application server', 8, 32.0, 200, '["Windows Server", "Oracle", "VMware"]');

-- Insert sample licenses
INSERT OR IGNORE INTO licenses (name, vendor, type, total, used, cost, expiry_date, status) VALUES
('VMware vSphere Standard', 'VMware', 'Perpetual', 10, 3, 5000.00, NULL, 'active'),
('Windows Server 2022', 'Microsoft', 'Subscription', 20, 12, 1200.00, '2025-12-31', 'active'),
('Prometheus Enterprise', 'Prometheus', 'Subscription', 5, 1, 2400.00, '2025-06-30', 'expiring'),
('Red Hat Enterprise Linux', 'Red Hat', 'Subscription', 15, 8, 3600.00, '2025-09-15', 'active'),
('Zabbix Professional', 'Zabbix', 'Subscription', 3, 2, 1800.00, '2025-03-20', 'active');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_vm_metrics_collected_at ON vm_metrics(collected_at);
CREATE INDEX IF NOT EXISTS idx_vm_metrics_vm_name ON vm_metrics(vm_name);
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_analytics_data_metric_name ON analytics_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health(component);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
