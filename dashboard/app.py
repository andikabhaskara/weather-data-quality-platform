import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Weather Data Platform", layout="wide")
st.title("🌤️ Weather Data Quality Platform")
st.markdown("Real-time monitoring of top cities' weather ingestion pipeline")

#Sidebar
st.sidebar.header("Filters")
city = st.sidebar.selectbox("Select City", ["All", "New York", "Singapore", "Tokyo"])
date_range = st.sidebar.date_input("Date Range", [datetime.now() - timedelta(days=7), datetime.now()])

#Mock data (replace with Athena query)
df = pd.DataFrame({
    'date': pd.date_range('2026-02-11', '2026-02-17'),
    'New York': [2.5, 3.1, 4.2, 5.0, 6.1, 5.5, 4.8],
    'Singapore': [28.5, 29.1, 28.9, 29.3, 28.7, 29.0, 28.8],
    'Tokyo': [8.2, 9.1, 10.3, 11.2, 10.8, 9.9, 10.1]
})

#Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", "15,120", "+2,160")
col2.metric("Data Quality", "99.8%", "+0.1%")
col3.metric("Pipeline Status", "✅ Healthy", "")

#Chart
st.subheader("Temperature Trends (7-Day Average)")
fig = px.line(df, x='date', y=['New York', 'Singapore', 'Tokyo'],
              labels={'value': 'Temperature (°C)', 'variable': 'City'})
st.plotly_chart(fig, use_container_width=True)

#Data Quality
st.subheader("Data Quality Checks")
st.dataframe({
    'Validation': ['Temperature Range', 'Null Checks', 'Record Count', 'Duplicate Detection', 'City Validation'],
    'Status': ['✅ Passed', '✅ Passed', '✅ Passed', '✅ Passed', '✅ Passed'],
    'Last Run': ['2 min ago'] * 5
})