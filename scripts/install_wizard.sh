
#!/bin/bash

echo "🧠 Welcome to the IROA Installation Wizard"

echo "1. Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "2. Setting up database..."
read -p "Enter PostgreSQL host [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Enter PostgreSQL port [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "Enter DB name [iroa_db]: " DB_NAME
DB_NAME=${DB_NAME:-iroa_db}

read -p "Enter DB user [iroa_user]: " DB_USER
DB_USER=${DB_USER:-iroa_user}

read -s -p "Enter DB password: " DB_PASSWORD
echo

echo "Creating .env file..."
cat <<EOT > .env
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
MONITOR_INTERVAL=60
PROMETHEUS_URL=http://localhost:9090
EOT

echo "3. Launching FastAPI backend..."
uvicorn api.main:app --reload
