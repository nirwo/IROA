from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Create a separate router for cluster-based features
cluster_router = APIRouter()

# Import the main routes to access shared data
import sys
import os
sys.path.append('/app')

@cluster_router.get("/capacity/clusters")
async def get_cluster_capacity_analysis():
    """Get capacity analysis broken down by compute clusters"""
    try:
        # Import the get_all_vms function
        from routes import get_all_vms
        
        # Get all VMs and group by cluster
        all_vms = await get_all_vms()
        clusters = {}
        
        for vm in all_vms:
            cluster_name = vm.get('cluster', 'Unknown')
            if cluster_name not in clusters:
                clusters[cluster_name] = {
                    'name': cluster_name,
                    'vms': [],
                    'total_cpu': 0,
                    'total_memory': 0,
                    'total_vms': 0
                }
            
            clusters[cluster_name]['vms'].append(vm)
            clusters[cluster_name]['total_cpu'] += vm.get('cores', 0)
            clusters[cluster_name]['total_memory'] += vm.get('memory', 0)
            clusters[cluster_name]['total_vms'] += 1
        
        # Calculate capacity for each cluster
        cluster_analysis = []
        for cluster_name, cluster_data in clusters.items():
            if cluster_data['total_vms'] > 0:
                avg_cpu = sum(vm.get('cpu', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                avg_memory = sum(vm.get('memory_usage', 0) for vm in cluster_data['vms']) / cluster_data['total_vms']
                
                # Calculate capacity with 80% utilization rule
                max_additional_vms = 0
                limiting_factor = "CPU"
                
                if cluster_data['total_cpu'] > 0:
                    cpu_capacity = int((cluster_data['total_cpu'] * 0.8) / 2) - cluster_data['total_vms']
                    memory_capacity = int((cluster_data['total_memory'] * 0.8) / 4) - cluster_data['total_vms']
                    
                    max_additional_vms = max(0, min(cpu_capacity, memory_capacity))
                    limiting_factor = "CPU" if cpu_capacity < memory_capacity else "Memory"
                
                cluster_analysis.append({
                    'cluster': cluster_name,
                    'current_vms': cluster_data['total_vms'],
                    'total_cpu_cores': cluster_data['total_cpu'],
                    'total_memory_gb': cluster_data['total_memory'],
                    'avg_cpu_usage': round(avg_cpu, 1),
                    'avg_memory_usage': round(avg_memory, 1),
                    'max_additional_vms': max_additional_vms,
                    'limiting_factor': limiting_factor,
                    'cpu_utilization': round((cluster_data['total_vms'] * 2) / max(cluster_data['total_cpu'], 1) * 100, 1),
                    'memory_utilization': round((cluster_data['total_vms'] * 4) / max(cluster_data['total_memory'], 1) * 100, 1)
                })
        
        return {
            'clusters': cluster_analysis,
            'total_clusters': len(cluster_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in cluster capacity analysis: {e}")
        return {
            'clusters': [],
            'total_clusters': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@cluster_router.get("/search")
async def search_assets(q: str = "", type: str = "all"):
    """Search through VMs and other visible assets"""
    try:
        from routes import get_all_vms, vcenter_inventory_cache
        results = []
        
        # Search VMs
        if type in ["all", "vm", "vms"]:
            all_vms = await get_all_vms()
            for vm in all_vms:
                vm_name = vm.get('vm', '').lower()
                cluster = vm.get('cluster', '').lower()
                source = vm.get('source', '').lower()
                
                if (q.lower() in vm_name or 
                    q.lower() in cluster or 
                    q.lower() in source):
                    results.append({
                        'type': 'vm',
                        'name': vm.get('vm'),
                        'cluster': vm.get('cluster'),
                        'source': vm.get('source'),
                        'status': vm.get('status'),
                        'cpu': vm.get('cpu'),
                        'memory': vm.get('memory'),
                        'details': vm.get('details', {})
                    })
        
        # Search Infrastructure
        if type in ["all", "infrastructure", "infra"]:
            try:
                infra_data = vcenter_inventory_cache
                for item in infra_data:
                    item_name = item.get('name', '').lower()
                    item_type = item.get('type', '').lower()
                    
                    if q.lower() in item_name or q.lower() in item_type:
                        results.append({
                            'type': 'infrastructure',
                            'name': item.get('name'),
                            'item_type': item.get('type'),
                            'status': item.get('status'),
                            'details': item.get('details', {})
                        })
            except:
                pass
        
        return {
            'query': q,
            'search_type': type,
            'results': results,
            'total_results': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in search: {e}")
        return {
            'query': q,
            'search_type': type,
            'results': [],
            'total_results': 0,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# Admin Workflow Management endpoints
class WorkflowView(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    clusters: List[str]
    view_type: str  # 'capacity', 'profile', 'monitoring'
    filters: dict
    created_by: str
    created_at: Optional[str] = None

# In-memory storage for workflow views
workflow_views_cache = [
    {
        "id": 1,
        "name": "Production Monitoring",
        "description": "Monitor production clusters only",
        "clusters": ["Production-Cluster"],
        "view_type": "monitoring",
        "filters": {"status": "running", "min_cpu": 0},
        "created_by": "admin",
        "created_at": "2025-07-26T20:00:00Z"
    },
    {
        "id": 2,
        "name": "Development Capacity",
        "description": "Capacity planning for development environments",
        "clusters": ["Development-Cluster"],
        "view_type": "capacity",
        "filters": {"utilization_threshold": 80},
        "created_by": "admin",
        "created_at": "2025-07-26T20:05:00Z"
    }
]

@cluster_router.get("/admin/workflows")
async def get_workflow_views():
    """Get all admin-created workflow views"""
    try:
        return {
            "workflows": workflow_views_cache,
            "total": len(workflow_views_cache),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflows: {str(e)}")

@cluster_router.post("/admin/workflows")
async def create_workflow_view(workflow: WorkflowView):
    """Create a new admin workflow view"""
    try:
        # Generate new ID
        new_id = max([w["id"] for w in workflow_views_cache], default=0) + 1
        
        new_workflow = {
            "id": new_id,
            "name": workflow.name,
            "description": workflow.description,
            "clusters": workflow.clusters,
            "view_type": workflow.view_type,
            "filters": workflow.filters,
            "created_by": workflow.created_by,
            "created_at": datetime.now().isoformat()
        }
        
        workflow_views_cache.append(new_workflow)
        print(f"✅ Created new workflow view: {workflow.name}")
        
        return new_workflow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@cluster_router.get("/admin/workflows/{workflow_id}/data")
async def get_workflow_data(workflow_id: int):
    """Get data for a specific workflow view"""
    try:
        # Find the workflow
        workflow = next((w for w in workflow_views_cache if w["id"] == workflow_id), None)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get data based on workflow type and filters
        if workflow["view_type"] == "capacity":
            # Get cluster capacity data filtered by workflow clusters
            cluster_data = await get_cluster_capacity_analysis()
            filtered_clusters = [
                cluster for cluster in cluster_data["clusters"]
                if cluster["cluster"] in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "clusters": filtered_clusters,
                    "total_clusters": len(filtered_clusters)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        elif workflow["view_type"] == "monitoring":
            # Get VMs filtered by workflow clusters
            from routes import get_all_vms
            all_vms = await get_all_vms()
            filtered_vms = [
                vm for vm in all_vms
                if vm.get("cluster") in workflow["clusters"]
            ]
            return {
                "workflow": workflow,
                "data": {
                    "vms": filtered_vms,
                    "total_vms": len(filtered_vms)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "workflow": workflow,
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow data: {str(e)}")

@cluster_router.delete("/admin/workflows/{workflow_id}")
async def delete_workflow_view(workflow_id: int):
    """Delete an admin workflow view"""
    try:
        global workflow_views_cache
        original_count = len(workflow_views_cache)
        workflow_views_cache = [w for w in workflow_views_cache if w["id"] != workflow_id]
        
        if len(workflow_views_cache) == original_count:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        print(f"✅ Deleted workflow view ID: {workflow_id}")
        return {"message": f"Workflow {workflow_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")
