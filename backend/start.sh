#!/bin/bash

# 1. Start FastAPI backend on port 8000
# We use & to run it in the background
echo "Starting FastAPI Backend..."
#uvicorn backend.server:app --host 0.0.0.0 --port 8000 &
gunicorn backend.server:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 &

# 2. Start Streamlit frontend on the port Render provides (default 10000)
echo "Starting Streamlit Frontend..."
streamlit run frontend/Add_Update.py --server.port 10000 --server.address 0.0.0.0