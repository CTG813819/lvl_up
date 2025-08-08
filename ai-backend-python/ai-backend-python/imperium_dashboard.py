import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

API_BASE = "http://34.202.215.209:4000/api/imperium"  # Using EC2 instance URL

st.title("Imperium Growth & Actions Dashboard")

# Agent Metrics
st.header("Agent Metrics")
try:
    metrics = requests.get(f"{API_BASE}/persistence/agent-metrics").json()
    df_metrics = pd.DataFrame(metrics)
    st.dataframe(df_metrics)
except Exception as e:
    st.error(f"Failed to load agent metrics: {e}")

# Learning Cycles
st.header("Learning Cycles")
try:
    cycles = requests.get(f"{API_BASE}/cycles").json()
    df_cycles = pd.DataFrame(cycles)
    st.dataframe(df_cycles)
except Exception as e:
    st.error(f"Failed to load learning cycles: {e}")

# Growth Over Time
st.header("Growth Over Time")
try:
    if not df_cycles.empty and 'start_time' in df_cycles.columns:
        # Handle different date formats and missing values
        df_cycles['start_time'] = pd.to_datetime(df_cycles['start_time'], errors='coerce')
        df_cycles = df_cycles.dropna(subset=['start_time'])
        
        if not df_cycles.empty and 'total_learning_value' in df_cycles.columns:
            # Convert to numeric, handling any non-numeric values
            df_cycles['total_learning_value'] = pd.to_numeric(df_cycles['total_learning_value'], errors='coerce').fillna(0)
            growth = df_cycles.groupby(df_cycles['start_time'].dt.date)['total_learning_value'].sum().cumsum()
            st.line_chart(growth)
        else:
            st.info("No learning value data available for plotting.")
    else:
        st.info("No learning cycles data available.")
except Exception as e:
    st.error(f"Failed to plot growth: {e}")
    st.info("Please check if the backend API is running and accessible.")

# Actions Table
st.header("Actions Log (Recent)")
try:
    logs = requests.get(f"{API_BASE}/persistence/learning-analytics").json()
    df_logs = pd.DataFrame(logs)
    st.dataframe(df_logs)
except Exception as e:
    st.error(f"Failed to load actions log: {e}") 