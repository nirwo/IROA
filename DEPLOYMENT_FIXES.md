# IROA System Deployment Fixes & Solutions

## Overview
This document details all the issues encountered during IROA system deployment and their solutions.

## 🔧 Infrastructure Fixes

### 1. PostgreSQL Port Conflicts
**Issue**: Port 5432 was already in use by existing PostgreSQL service
**Solution**: 
- Modified `docker-compose.yml` to use port 5434
- Updated `.env` file to match new port configuration
```yaml
# docker-compose.yml
ports:
  - "5434:5432"
```

### 2. Prometheus Configuration Missing
**Issue**: `prometheus.yml` was a directory instead of configuration file
**Solution**: 
- Removed empty directory
- Created proper Prometheus configuration file with scrape configs
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'iroa-api'
    static_configs:
      - targets: ['iroa-api:8000']
```

### 3. API Port Conflicts
**Issue**: Port 8000 was occupied by Docker services
**Solution**: Changed FastAPI server to port 8001
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

## 🐍 Python/Backend Fixes

### 4. Module Import Issues
**Issue**: Python modules not found due to path issues
**Solution**: Added proper path configuration in test files
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### 5. Pandas DataFrame Creation Bug
**Issue**: TypeError in ML forecast function with pandas DataFrame
**Solution**: Simplified to use numpy arrays directly
```python
# Before (broken)
data = [(m.timestamp, m.cpu_usage) for m in metrics]
df = pd.DataFrame(data, columns=["timestamp", "cpu_usage"])

# After (working)
cpu_values = [m.cpu_usage for m in metrics]
time_indices = list(range(len(cpu_values)))
X = np.array(time_indices).reshape(-1, 1)
y = np.array(cpu_values)
```

### 6. Anomaly Detection Pandas Issues
**Issue**: Similar pandas compatibility problems
**Solution**: Replaced pandas with pure numpy implementation
```python
# Extract features without pandas
features = []
for m in metrics:
    features.append([m.cpu_usage, m.memory_usage, m.disk_io, m.net_io])

X = np.array(features)
model = IsolationForest(contamination=0.1, random_state=42)
anomaly_labels = model.fit_predict(X)
```

### 7. Database Initialization
**Issue**: No database tables or sample data
**Solution**: Created `scripts/init_db.py` with:
- Table creation using SQLAlchemy
- Mock VM data generation
- 7 days of realistic metrics data

### 8. Chatbot Import Dependencies
**Issue**: Streamlit chatbot couldn't import recommendation engine
**Solution**: Modified to use API calls instead of direct imports
```python
# Before
from recommendation.engine import generate_recommendations

# After
import requests
response = requests.get("http://localhost:8001/recommendations")
```

## 🎨 Frontend Fixes

### 9. Missing Node.js Dependencies
**Issue**: No package.json or proper Vue.js setup
**Solution**: Created complete Vue.js + Vite setup
```json
{
  "dependencies": {
    "vue": "^3.3.4",
    "axios": "^1.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.4",
    "vite": "^4.4.9"
  }
}
```

### 10. API Endpoint Mismatch
**Issue**: Frontend calling wrong API port
**Solution**: Updated App.vue to use correct port 8001

### 11. Streamlit Port Conflicts
**Issue**: Default Streamlit port 8501 was occupied
**Solution**: Used port 8502 for chatbot

## 🧪 Testing Fixes

### 12. Test Module Imports
**Issue**: Tests couldn't find modules
**Solution**: Added proper Python path configuration

### 13. Git Repository Missing
**Issue**: No version control
**Solution**: Initialized git repo and committed all changes

## 📊 Performance Optimizations

### 14. ML Model Efficiency
- Simplified linear regression without pandas overhead
- Added proper error handling for insufficient data
- Optimized database queries with proper indexing

### 15. API Response Format
- Standardized JSON responses
- Added proper error handling
- Included detailed metrics in responses

## 🔒 Security Considerations

### 16. Database Configuration
- Used environment variables for sensitive data
- Proper connection pooling
- Parameterized queries to prevent SQL injection

### 17. API Security
- Added CORS middleware
- Input validation on endpoints
- Proper error handling without exposing internals

## 📈 Monitoring Setup

### 18. Prometheus Integration
- Created proper scrape configurations
- Added API metrics endpoints
- Configured for Docker networking

## 🚀 Deployment Architecture

Final working architecture:
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Prometheus    │    │   FastAPI       │
│   Port: 5434    │    │   Port: 9090    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   Streamlit     │    │   Browser       │
│   Port: 3000    │    │   Port: 8502    │    │   Previews      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✅ Verification Commands

Test all components:
```bash
# API Health
curl http://localhost:8001/health

# Recommendations
curl http://localhost:8001/recommendations

# Forecast
curl http://localhost:8001/forecast/1

# Anomalies
curl http://localhost:8001/anomalies/1

# Run tests
pytest tests/test_engine.py -v
```

## 🎯 Key Lessons Learned

1. **Port Management**: Always check for port conflicts in development
2. **Pandas Compatibility**: Newer pandas versions can have breaking changes
3. **Path Management**: Python module imports need careful path handling
4. **Docker Networking**: Container communication requires proper configuration
5. **API Design**: Consistent error handling and response formats are crucial
6. **Testing**: Proper test setup prevents deployment issues
7. **Documentation**: Clear setup instructions save debugging time

## 🔄 Future Improvements

1. Add comprehensive logging
2. Implement authentication/authorization
3. Add more sophisticated ML models
4. Create automated deployment scripts
5. Add comprehensive monitoring dashboards
6. Implement real-time WebSocket updates
