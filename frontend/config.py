import os

import streamlit as st


def get_api_url() -> str:
    """
    Base URL of the FastAPI backend.

    Priority:
    1) Streamlit secrets: API_URL
    2) Environment variable: API_URL
    3) Local default: http://localhost:8000
    """
    try:
        secret_url = st.secrets.get("API_URL")
    except Exception:
        secret_url = None

    url = (secret_url or os.environ.get("API_URL") or "http://localhost:8000").strip()
    return url[:-1] if url.endswith("/") else url

