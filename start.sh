#!/bin/bash

# 1. Start Backend
# We add current directory to PYTHONPATH so it finds the 'backend' folder
export PYTHONPATH=$PYTHONPATH:.

echo "Starting FastAPI Backend with Gunicorn..."
gunicorn backend.server:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &

# 2. Wait for backend to stabilize
sleep 5

# 3. Start Frontend
echo "Starting Streamlit Frontend..."
streamlit run frontend/Add_Update.py --server.port 10000 --server.address 0.0.0.0
