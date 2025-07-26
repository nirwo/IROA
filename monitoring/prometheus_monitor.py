
import requests
from config.config import settings
from datetime import datetime

def fetch_prometheus_metrics():
    try:
        query = 'rate(node_cpu_seconds_total{mode!="idle"}[1m])'
        response = requests.get(f"{settings.PROMETHEUS_URL}/api/v1/query", params={'query': query})
        result = response.json()
        metrics = []

        for item in result['data']['result']:
            instance = item['metric'].get('instance', 'unknown')
            value = float(item['value'][1])
            metrics.append({
                "instance": instance,
                "cpu_usage": round(value * 100, 2),
                "timestamp": datetime.utcnow()
            })

        return metrics
    except Exception as e:
        print(f"[!] Error fetching Prometheus metrics: {e}")
        return []
