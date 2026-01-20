import os
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Books Dashboard", layout="wide")


DEFAULT_API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")


st.sidebar.title("Configurações")
API_BASE = st.sidebar.text_input("API Base URL", value=DEFAULT_API_BASE)

st.title(" Books API — Dashboard")

col1, col2, col3 = st.columns(3)


try:
    r = requests.get(f"{API_BASE}/api/v1/health", timeout=10)
    r.raise_for_status()
    health = r.json()
    col1.metric("API Status", health.get("status", "error"))
except Exception as e:
    col1.metric("API Status", "offline")
    st.error(f"Erro health: {e}")


try:
    r = requests.get(f"{API_BASE}/api/v1/metrics", timeout=10)
    r.raise_for_status()
    metrics = r.json()
    col2.metric("Requests total", metrics.get("requests_total", 0))
    col3.metric("Avg latency (ms)", metrics.get("avg_latency_ms", 0.0))
except Exception as e:
    st.error(f"Erro métricas: {e}")

st.divider()

st.subheader(" Livros (API)")


try:
    r = requests.get(f"{API_BASE}/api/v1/books", timeout=60)
    r.raise_for_status()
    books = r.json()

    df = pd.DataFrame(books)

    st.metric("Total de livros retornados", len(df))
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Erro carregando livros: {e}")
