
# 🧠 IROA - Intelligent Resource Optimization Agent

## Overview
IROA helps companies monitor, analyze, and optimize the usage of virtual infrastructure (VMs, storage, CPU, memory). It includes:
- Real-time Prometheus and vCenter monitoring
- Analysis of VM trends and underutilization
- Recommendations for resource resizing or shutdown
- Dashboard and chatbot for insights
- Optional automation engine

## Stack
- Backend: Python (FastAPI, SQLAlchemy)
- Frontend: Vue.js + Tailwind
- Chatbot: Streamlit
- Automation: PowerCLI, SSH
- DB: PostgreSQL

## Getting Started
1. Configure `.env` file with DB and Prometheus details
2. Run FastAPI backend:
    ```bash
    uvicorn api.main:app --reload
    ```
3. Start Vue frontend:
    ```bash
    cd dashboard
    npm install
    npm run dev
    ```
4. Run chatbot:
    ```bash
    streamlit run dashboard/ChatbotAssistant.py
    ```

## Test
```bash
pytest tests/test_engine.py
```
