-- Workload and License Management Database Schema

-- Workload Groups (Admin-defined clusters for customer-facing names)
CREATE TABLE IF NOT EXISTS workload_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    customer_visible BOOLEAN DEFAULT 1,
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Workload Group to Cluster Mapping (Many-to-many)
CREATE TABLE IF NOT EXISTS workload_cluster_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_group_id INTEGER,
    cluster_name TEXT NOT NULL,
    cluster_source TEXT DEFAULT 'vcenter', -- vcenter, hyperv
    allocation_weight REAL DEFAULT 1.0, -- For resource distribution
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workload_group_id) REFERENCES workload_groups(id) ON DELETE CASCADE
);

-- License Types
CREATE TABLE IF NOT EXISTS license_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    vendor TEXT NOT NULL,
    product TEXT NOT NULL,
    os_compatibility TEXT, -- ubuntu, windows, rhel, etc.
    license_model TEXT, -- per_user, per_device, per_core, concurrent
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- License Pools
CREATE TABLE IF NOT EXISTS license_pools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_type_id INTEGER,
    workload_group_id INTEGER,
    total_licenses INTEGER DEFAULT 0,
    allocated_licenses INTEGER DEFAULT 0,
    available_licenses INTEGER GENERATED ALWAYS AS (total_licenses - allocated_licenses) STORED,
    cost_per_license REAL DEFAULT 0.0,
    renewal_date DATE,
    vendor_contract_id TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (license_type_id) REFERENCES license_types(id),
    FOREIGN KEY (workload_group_id) REFERENCES workload_groups(id)
);

-- VM Profiles (Template-based workload definitions)
CREATE TABLE IF NOT EXISTS vm_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_group_id INTEGER,
    profile_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    cpu_cores INTEGER NOT NULL,
    memory_gb INTEGER NOT NULL,
    storage_gb INTEGER NOT NULL,
    os_type TEXT NOT NULL, -- ubuntu, windows, rhel
    os_version TEXT,
    required_licenses TEXT, -- JSON array of license_type_ids
    estimated_cost_monthly REAL DEFAULT 0.0,
    utilization_factor REAL DEFAULT 0.7, -- Expected utilization ratio
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (workload_group_id) REFERENCES workload_groups(id)
);

-- Workload Capacity Analysis
CREATE TABLE IF NOT EXISTS workload_capacity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workload_group_id INTEGER,
    total_cpu_cores INTEGER DEFAULT 0,
    total_memory_gb INTEGER DEFAULT 0,
    total_storage_gb INTEGER DEFAULT 0,
    allocated_cpu_cores INTEGER DEFAULT 0,
    allocated_memory_gb INTEGER DEFAULT 0,
    allocated_storage_gb INTEGER DEFAULT 0,
    available_cpu_cores INTEGER GENERATED ALWAYS AS (total_cpu_cores - allocated_cpu_cores) STORED,
    available_memory_gb INTEGER GENERATED ALWAYS AS (total_memory_gb - allocated_memory_gb) STORED,
    available_storage_gb INTEGER GENERATED ALWAYS AS (total_storage_gb - allocated_storage_gb) STORED,
    max_additional_vms INTEGER DEFAULT 0,
    utilization_cpu_percent REAL DEFAULT 0.0,
    utilization_memory_percent REAL DEFAULT 0.0,
    utilization_storage_percent REAL DEFAULT 0.0,
    last_calculated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workload_group_id) REFERENCES workload_groups(id),
    UNIQUE(workload_group_id)
);

-- License Allocations (Track which VMs use which licenses)
CREATE TABLE IF NOT EXISTS license_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_pool_id INTEGER,
    vm_id TEXT, -- Reference to infrastructure_vms.vm_id
    vm_name TEXT,
    workload_group_id INTEGER,
    allocated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deallocated_at DATETIME,
    allocation_type TEXT DEFAULT 'automatic', -- automatic, manual
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (license_pool_id) REFERENCES license_pools(id),
    FOREIGN KEY (workload_group_id) REFERENCES workload_groups(id)
);

-- Smart Filtering Configurations
CREATE TABLE IF NOT EXISTS smart_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filter_name TEXT NOT NULL,
    page_type TEXT NOT NULL, -- vms, capacity, profiles, licenses
    filter_criteria TEXT NOT NULL, -- JSON object with filter rules
    created_by TEXT,
    is_shared BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default license types
INSERT OR IGNORE INTO license_types (name, vendor, product, os_compatibility, license_model, description) VALUES
('Citrix Virtual Apps', 'Citrix', 'Virtual Apps and Desktops', 'windows', 'concurrent', 'Citrix Virtual Apps concurrent user licenses'),
('Citrix One Identity', 'Citrix', 'One Identity', 'ubuntu,rhel', 'per_user', 'Citrix One Identity user licenses for Linux systems'),
('Lakeside SysTrack', 'Lakeside', 'SysTrack', 'windows', 'per_device', 'Lakeside SysTrack device monitoring licenses'),
('Windows Server', 'Microsoft', 'Windows Server', 'windows', 'per_core', 'Windows Server core-based licensing'),
('Ubuntu Pro', 'Canonical', 'Ubuntu Pro', 'ubuntu', 'per_device', 'Ubuntu Pro support and security licenses');

-- Insert default workload groups
INSERT OR IGNORE INTO workload_groups (name, display_name, description, customer_visible) VALUES
('production', 'Production Environment', 'Production workloads and critical applications', 1),
('development', 'Development Environment', 'Development and testing workloads', 1),
('staging', 'Staging Environment', 'Pre-production staging environment', 1),
('training', 'Training Environment', 'Training and demo systems', 1);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workload_cluster_mapping_workload ON workload_cluster_mapping(workload_group_id);
CREATE INDEX IF NOT EXISTS idx_workload_cluster_mapping_cluster ON workload_cluster_mapping(cluster_name);
CREATE INDEX IF NOT EXISTS idx_license_pools_workload ON license_pools(workload_group_id);
CREATE INDEX IF NOT EXISTS idx_license_allocations_pool ON license_allocations(license_pool_id);
CREATE INDEX IF NOT EXISTS idx_license_allocations_vm ON license_allocations(vm_id);
CREATE INDEX IF NOT EXISTS idx_vm_profiles_workload ON vm_profiles(workload_group_id);
CREATE INDEX IF NOT EXISTS idx_smart_filters_page ON smart_filters(page_type);

-- Create triggers to update timestamps
CREATE TRIGGER IF NOT EXISTS update_workload_groups_timestamp 
    AFTER UPDATE ON workload_groups
    FOR EACH ROW
BEGIN
    UPDATE workload_groups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_license_pools_timestamp 
    AFTER UPDATE ON license_pools
    FOR EACH ROW
BEGIN
    UPDATE license_pools SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_vm_profiles_timestamp 
    AFTER UPDATE ON vm_profiles
    FOR EACH ROW
BEGIN
    UPDATE vm_profiles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Create trigger to update allocated licenses count
CREATE TRIGGER IF NOT EXISTS update_allocated_licenses_count
    AFTER INSERT ON license_allocations
    FOR EACH ROW
    WHEN NEW.is_active = 1
BEGIN
    UPDATE license_pools 
    SET allocated_licenses = (
        SELECT COUNT(*) 
        FROM license_allocations 
        WHERE license_pool_id = NEW.license_pool_id AND is_active = 1
    )
    WHERE id = NEW.license_pool_id;
END;

CREATE TRIGGER IF NOT EXISTS update_deallocated_licenses_count
    AFTER UPDATE ON license_allocations
    FOR EACH ROW
    WHEN OLD.is_active = 1 AND NEW.is_active = 0
BEGIN
    UPDATE license_pools 
    SET allocated_licenses = (
        SELECT COUNT(*) 
        FROM license_allocations 
        WHERE license_pool_id = NEW.license_pool_id AND is_active = 1
    )
    WHERE id = NEW.license_pool_id;
END;