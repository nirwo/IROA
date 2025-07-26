
from analysis.engine import get_underutilized_vms

def generate_recommendations():
    recommendations = []
    underutilized_vms = get_underutilized_vms()

    for vm_data in underutilized_vms:
        recommendation = {
            "vm": vm_data["vm"],
            "reason": "Underutilized VM",
            "suggestion": f"Consider resizing or shutting down. Avg CPU: {vm_data['avg_cpu']}%, Avg Mem: {vm_data['avg_mem']}%",
            "details": vm_data
        }
        recommendations.append(recommendation)

    return recommendations
