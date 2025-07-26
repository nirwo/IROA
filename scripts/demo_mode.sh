
#!/bin/bash

echo "🚀 Running IROA in DEMO MODE..."

echo "Starting FastAPI backend on port 8000..."
uvicorn api.main:app --port 8000 &

sleep 3
echo "Fetching recommendations (mocked)..."
curl http://localhost:8000/recommendations

echo "Opening Chatbot (Streamlit)..."
streamlit run dashboard/ChatbotAssistant.py
