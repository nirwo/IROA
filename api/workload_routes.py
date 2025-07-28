"""
IROA Workload and License Management Routes
Handles workload groups, license management, and smart filtering
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class WorkloadGroup(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    customer_visible: bool = True

class WorkloadGroupUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    customer_visible: Optional[bool] = None

class ClusterMapping(BaseModel):
    cluster_name: str
    cluster_source: str = "vcenter"
    allocation_weight: float = 1.0

class LicensePool(BaseModel):
    license_type_id: int
    workload_group_id: int
    total_licenses: int
    cost_per_license: float = 0.0
    renewal_date: Optional[date] = None
    vendor_contract_id: Optional[str] = None
    notes: Optional[str] = None

class VMProfile(BaseModel):
    workload_group_id: int
    profile_name: str
    display_name: str
    description: Optional[str] = None
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    os_type: str
    os_version: Optional[str] = None
    required_licenses: List[int] = []
    estimated_cost_monthly: float = 0.0
    utilization_factor: float = 0.7

class SmartFilter(BaseModel):
    filter_name: str
    page_type: str
    filter_criteria: Dict[str, Any]
    is_shared: bool = False

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect("data/iroa.db")
    conn.row_factory = sqlite3.Row
    return conn

# Workload Groups Management
@router.get("/workload-groups")
async def get_workload_groups(customer_view: bool = Query(False)):
    """Get all workload groups"""
    try:
        with get_db_connection() as conn:
            if customer_view:
                # Customer view - only show customer-visible groups
                cursor = conn.execute("""
                    SELECT wg.*, 
                           COUNT(wcm.cluster_name) as cluster_count,
                           wc.total_cpu_cores, wc.total_memory_gb, wc.total_storage_gb,
                           wc.available_cpu_cores, wc.available_memory_gb, wc.available_storage_gb
                    FROM workload_groups wg
                    LEFT JOIN workload_cluster_mapping wcm ON wg.id = wcm.workload_group_id AND wcm.is_active = 1
                    LEFT JOIN workload_capacity wc ON wg.id = wc.workload_group_id
                    WHERE wg.is_active = 1 AND wg.customer_visible = 1
                    GROUP BY wg.id
                    ORDER BY wg.display_name
                """)
            else:
                # Admin view - show all groups
                cursor = conn.execute("""
                    SELECT wg.*, 
                           COUNT(wcm.cluster_name) as cluster_count,
                           wc.total_cpu_cores, wc.total_memory_gb, wc.total_storage_gb,
                           wc.available_cpu_cores, wc.available_memory_gb, wc.available_storage_gb
                    FROM workload_groups wg
                    LEFT JOIN workload_cluster_mapping wcm ON wg.id = wcm.workload_group_id AND wcm.is_active = 1
                    LEFT JOIN workload_capacity wc ON wg.id = wc.workload_group_id
                    WHERE wg.is_active = 1
                    GROUP BY wg.id
                    ORDER BY wg.display_name
                """)
            
            workload_groups = [dict(row) for row in cursor.fetchall()]
            return {"workload_groups": workload_groups}
            
    except Exception as e:
        logger.error(f"Error getting workload groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workload-groups")
async def create_workload_group(workload_group: WorkloadGroup):
    """Create a new workload group"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO workload_groups (name, display_name, description, customer_visible, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (workload_group.name, workload_group.display_name, workload_group.description,
                  workload_group.customer_visible, "api_user"))
            
            workload_group_id = cursor.lastrowid
            conn.commit()
            
            return {"message": "Workload group created successfully", "id": workload_group_id}
            
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Workload group name already exists")
    except Exception as e:
        logger.error(f"Error creating workload group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/workload-groups/{group_id}")
async def update_workload_group(group_id: int, workload_group: WorkloadGroupUpdate):
    """Update a workload group"""
    try:
        with get_db_connection() as conn:
            # Build dynamic update query
            updates = []
            values = []
            
            if workload_group.display_name is not None:
                updates.append("display_name = ?")
                values.append(workload_group.display_name)
            
            if workload_group.description is not None:
                updates.append("description = ?")
                values.append(workload_group.description)
                
            if workload_group.customer_visible is not None:
                updates.append("customer_visible = ?")
                values.append(workload_group.customer_visible)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            values.append(group_id)
            query = f"UPDATE workload_groups SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND is_active = 1"
            
            cursor = conn.execute(query, values)
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Workload group not found")
            
            conn.commit()
            return {"message": "Workload group updated successfully"}
            
    except Exception as e:
        logger.error(f"Error updating workload group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workload-groups/{group_id}/clusters")
async def add_cluster_to_workload(group_id: int, cluster_mapping: ClusterMapping):
    """Add a cluster to a workload group"""
    try:
        with get_db_connection() as conn:
            # Check if workload group exists
            wg_check = conn.execute("SELECT id FROM workload_groups WHERE id = ? AND is_active = 1", (group_id,)).fetchone()
            if not wg_check:
                raise HTTPException(status_code=404, detail="Workload group not found")
            
            # Check if mapping already exists
            existing = conn.execute("""
                SELECT id FROM workload_cluster_mapping 
                WHERE workload_group_id = ? AND cluster_name = ? AND is_active = 1
            """, (group_id, cluster_mapping.cluster_name)).fetchone()
            
            if existing:
                raise HTTPException(status_code=400, detail="Cluster already mapped to this workload group")
            
            cursor = conn.execute("""
                INSERT INTO workload_cluster_mapping 
                (workload_group_id, cluster_name, cluster_source, allocation_weight)
                VALUES (?, ?, ?, ?)
            """, (group_id, cluster_mapping.cluster_name, cluster_mapping.cluster_source, cluster_mapping.allocation_weight))
            
            conn.commit()
            return {"message": "Cluster added to workload group successfully", "mapping_id": cursor.lastrowid}
            
    except Exception as e:
        logger.error(f"Error adding cluster to workload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/workload-groups/{group_id}/clusters/{cluster_name}")
async def remove_cluster_from_workload(group_id: int, cluster_name: str):
    """Remove a cluster from a workload group"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                UPDATE workload_cluster_mapping 
                SET is_active = 0 
                WHERE workload_group_id = ? AND cluster_name = ? AND is_active = 1
            """, (group_id, cluster_name))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Cluster mapping not found")
            
            conn.commit()
            return {"message": "Cluster removed from workload group successfully"}
            
    except Exception as e:
        logger.error(f"Error removing cluster from workload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# License Management
@router.get("/license-types")
async def get_license_types():
    """Get all license types"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM license_types WHERE is_active = 1 ORDER BY vendor, product
            """)
            license_types = [dict(row) for row in cursor.fetchall()]
            return {"license_types": license_types}
            
    except Exception as e:
        logger.error(f"Error getting license types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/license-pools")
async def get_license_pools(workload_group_id: Optional[int] = Query(None)):
    """Get license pools"""
    try:
        with get_db_connection() as conn:
            if workload_group_id:
                cursor = conn.execute("""
                    SELECT lp.*, lt.name as license_type_name, lt.vendor, lt.product,
                           wg.display_name as workload_group_name
                    FROM license_pools lp
                    JOIN license_types lt ON lp.license_type_id = lt.id
                    JOIN workload_groups wg ON lp.workload_group_id = wg.id
                    WHERE lp.workload_group_id = ? AND lp.is_active = 1
                    ORDER BY lt.vendor, lt.product
                """, (workload_group_id,))
            else:
                cursor = conn.execute("""
                    SELECT lp.*, lt.name as license_type_name, lt.vendor, lt.product,
                           wg.display_name as workload_group_name
                    FROM license_pools lp
                    JOIN license_types lt ON lp.license_type_id = lt.id
                    JOIN workload_groups wg ON lp.workload_group_id = wg.id
                    WHERE lp.is_active = 1
                    ORDER BY wg.display_name, lt.vendor, lt.product
                """)
            
            license_pools = [dict(row) for row in cursor.fetchall()]
            return {"license_pools": license_pools}
            
    except Exception as e:
        logger.error(f"Error getting license pools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/license-pools")
async def create_license_pool(license_pool: LicensePool):
    """Create a new license pool"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO license_pools 
                (license_type_id, workload_group_id, total_licenses, cost_per_license, 
                 renewal_date, vendor_contract_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (license_pool.license_type_id, license_pool.workload_group_id,
                  license_pool.total_licenses, license_pool.cost_per_license,
                  license_pool.renewal_date, license_pool.vendor_contract_id,
                  license_pool.notes))
            
            pool_id = cursor.lastrowid
            conn.commit()
            
            return {"message": "License pool created successfully", "id": pool_id}
            
    except Exception as e:
        logger.error(f"Error creating license pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# VM Profiles Management
@router.get("/vm-profiles")
async def get_vm_profiles(workload_group_id: Optional[int] = Query(None)):
    """Get VM profiles"""
    try:
        with get_db_connection() as conn:
            if workload_group_id:
                cursor = conn.execute("""
                    SELECT vp.*, wg.display_name as workload_group_name
                    FROM vm_profiles vp
                    JOIN workload_groups wg ON vp.workload_group_id = wg.id
                    WHERE vp.workload_group_id = ? AND vp.is_active = 1
                    ORDER BY vp.profile_name
                """, (workload_group_id,))
            else:
                cursor = conn.execute("""
                    SELECT vp.*, wg.display_name as workload_group_name
                    FROM vm_profiles vp
                    JOIN workload_groups wg ON vp.workload_group_id = wg.id
                    WHERE vp.is_active = 1
                    ORDER BY wg.display_name, vp.profile_name
                """)
            
            profiles = []
            for row in cursor.fetchall():
                profile = dict(row)
                # Parse required licenses JSON
                if profile['required_licenses']:
                    try:
                        profile['required_licenses'] = json.loads(profile['required_licenses'])
                    except:
                        profile['required_licenses'] = []
                profiles.append(profile)
            
            return {"vm_profiles": profiles}
            
    except Exception as e:
        logger.error(f"Error getting VM profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vm-profiles")
async def create_vm_profile(vm_profile: VMProfile):
    """Create a new VM profile"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO vm_profiles 
                (workload_group_id, profile_name, display_name, description,
                 cpu_cores, memory_gb, storage_gb, os_type, os_version,
                 required_licenses, estimated_cost_monthly, utilization_factor, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vm_profile.workload_group_id, vm_profile.profile_name, vm_profile.display_name,
                  vm_profile.description, vm_profile.cpu_cores, vm_profile.memory_gb,
                  vm_profile.storage_gb, vm_profile.os_type, vm_profile.os_version,
                  json.dumps(vm_profile.required_licenses), vm_profile.estimated_cost_monthly,
                  vm_profile.utilization_factor, "api_user"))
            
            profile_id = cursor.lastrowid
            conn.commit()
            
            return {"message": "VM profile created successfully", "id": profile_id}
            
    except Exception as e:
        logger.error(f"Error creating VM profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Smart Filtering
@router.get("/smart-filters")
async def get_smart_filters(page_type: str = Query(...)):
    """Get smart filters for a specific page type"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM smart_filters 
                WHERE page_type = ? 
                ORDER BY filter_name
            """, (page_type,))
            
            filters = []
            for row in cursor.fetchall():
                filter_obj = dict(row)
                # Parse filter criteria JSON
                try:
                    filter_obj['filter_criteria'] = json.loads(filter_obj['filter_criteria'])
                except:
                    filter_obj['filter_criteria'] = {}
                filters.append(filter_obj)
            
            return {"smart_filters": filters}
            
    except Exception as e:
        logger.error(f"Error getting smart filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/smart-filters")
async def create_smart_filter(smart_filter: SmartFilter):
    """Create a new smart filter"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO smart_filters 
                (filter_name, page_type, filter_criteria, is_shared, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (smart_filter.filter_name, smart_filter.page_type,
                  json.dumps(smart_filter.filter_criteria), smart_filter.is_shared,
                  "api_user"))
            
            filter_id = cursor.lastrowid
            conn.commit()
            
            return {"message": "Smart filter created successfully", "id": filter_id}
            
    except Exception as e:
        logger.error(f"Error creating smart filter: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Capacity Calculation
@router.post("/workload-groups/{group_id}/calculate-capacity")
async def calculate_workload_capacity(group_id: int):
    """Calculate and update workload capacity from infrastructure data"""
    try:
        with get_db_connection() as conn:
            # Get clusters for this workload group
            cursor = conn.execute("""
                SELECT cluster_name, cluster_source, allocation_weight
                FROM workload_cluster_mapping
                WHERE workload_group_id = ? AND is_active = 1
            """, (group_id,))
            clusters = cursor.fetchall()
            
            if not clusters:
                raise HTTPException(status_code=404, detail="No clusters found for this workload group")
            
            total_cpu = 0
            total_memory = 0
            total_storage = 0
            allocated_cpu = 0
            allocated_memory = 0
            allocated_storage = 0
            
            # Calculate totals from infrastructure data
            for cluster in clusters:
                cluster_name = cluster['cluster_name']
                
                # Get cluster infrastructure data
                cluster_cursor = conn.execute("""
                    SELECT total_cpu_cores, total_memory_gb, used_cpu_mhz, used_memory_gb
                    FROM infrastructure_clusters
                    WHERE name = ? AND is_active = 1
                """, (cluster_name,))
                cluster_data = cluster_cursor.fetchone()
                
                if cluster_data:
                    weight = cluster['allocation_weight']
                    total_cpu += int((cluster_data['total_cpu_cores'] or 0) * weight)
                    total_memory += int((cluster_data['total_memory_gb'] or 0) * weight)
                    
                    # Estimate current usage
                    allocated_cpu += int((cluster_data['used_cpu_mhz'] or 0) / 2000 * weight)  # Rough conversion
                    allocated_memory += int((cluster_data['used_memory_gb'] or 0) * weight)
                
                # Get storage from datastores
                storage_cursor = conn.execute("""
                    SELECT SUM(capacity_gb) as total_storage, SUM(used_space_gb) as used_storage
                    FROM infrastructure_datastores
                    WHERE source = ? AND is_active = 1
                """, (cluster['cluster_source'],))
                storage_data = storage_cursor.fetchone()
                
                if storage_data:
                    weight = cluster['allocation_weight']
                    total_storage += int((storage_data['total_storage'] or 0) * weight)
                    allocated_storage += int((storage_data['used_storage'] or 0) * weight)
            
            # Calculate utilization percentages
            util_cpu = (allocated_cpu / total_cpu * 100) if total_cpu > 0 else 0
            util_memory = (allocated_memory / total_memory * 100) if total_memory > 0 else 0
            util_storage = (allocated_storage / total_storage * 100) if total_storage > 0 else 0
            
            # Estimate max additional VMs (conservative calculation)
            available_cpu = max(0, total_cpu - allocated_cpu)
            available_memory = max(0, total_memory - allocated_memory)
            
            # Assume average VM needs 2 cores and 4GB RAM
            max_vms_cpu = available_cpu // 2
            max_vms_memory = available_memory // 4
            max_additional_vms = min(max_vms_cpu, max_vms_memory)
            
            # Update or insert capacity data
            conn.execute("""
                INSERT OR REPLACE INTO workload_capacity
                (workload_group_id, total_cpu_cores, total_memory_gb, total_storage_gb,
                 allocated_cpu_cores, allocated_memory_gb, allocated_storage_gb,
                 max_additional_vms, utilization_cpu_percent, utilization_memory_percent,
                 utilization_storage_percent, last_calculated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (group_id, total_cpu, total_memory, total_storage,
                  allocated_cpu, allocated_memory, allocated_storage,
                  max_additional_vms, util_cpu, util_memory, util_storage))
            
            conn.commit()
            
            return {
                "message": "Workload capacity calculated successfully",
                "capacity": {
                    "total_cpu_cores": total_cpu,
                    "total_memory_gb": total_memory,
                    "total_storage_gb": total_storage,
                    "available_cpu_cores": available_cpu,
                    "available_memory_gb": available_memory,
                    "available_storage_gb": total_storage - allocated_storage,
                    "max_additional_vms": max_additional_vms,
                    "utilization_cpu_percent": round(util_cpu, 1),
                    "utilization_memory_percent": round(util_memory, 1),
                    "utilization_storage_percent": round(util_storage, 1)
                }
            }
            
    except Exception as e:
        logger.error(f"Error calculating workload capacity: {e}")
        raise HTTPException(status_code=500, detail=str(e))