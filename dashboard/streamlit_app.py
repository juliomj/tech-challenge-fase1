import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Books Dashboard", layout="wide")

API_BASE = st.sidebar.text_input("API Base URL", "http://127.0.0.1:5000")

st.title("📚 Books API — Dashboard")

col1, col2, col3 = st.columns(3)

try:
    health = requests.get(f"{API_BASE}/api/v1/health", timeout=10).json()
    col1.metric("API Status", health.get("status", "error"))
except Exception as e:
    col1.metric("API Status", "offline")
    st.error(e)

try:
    metrics = requests.get(f"{API_BASE}/api/v1/metrics", timeout=10).json()
    col2.metric("Requests total", metrics.get("requests_total", 0))
    col3.metric("Avg latency (ms)", metrics.get("avg_latency_ms", 0.0))
except Exception as e:
    st.error(f"Erro métricas: {e}")

st.divider()

st.subheader("📦 Livros (API)")

try:
    books = requests.get(f"{API_BASE}/api/v1/books", timeout=60).json()
    df = pd.DataFrame(books)

    st.metric("Total de livros retornados", len(df))
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Erro carregando livros: {e}")
