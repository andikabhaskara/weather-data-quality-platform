"""
Weather Data Quality Platform — Streamlit Dashboard

Architecture:
  data_loader.py handles WHERE data comes from (local files vs Athena)
  app.py handles WHAT the user sees (layout, charts, filters)
"""

import plotly.express as px
import streamlit as st
from data_loader import get_summary_metrics, load_local_data, run_quality_checks

# -- PAGE CONFIG --
st.set_page_config(page_title="Weather Data Quality Platform", layout="wide")
st.title("🌤️ Weather Data Quality Platform")
st.markdown("Real-time monitoring of weather data ingestion pipeline quality")

# -- LOAD DATA --
# Streamlit re-runs the entire script on every interaction.
# Without caching, it would re-read all JSON files on every click. cache_data
# memoizes the result and only reloads when the function code changes.
# ttl=300 = refresh every 5 minutes (in case new ingestion data arrives)


@st.cache_data(ttl=300)
def get_data():
    return load_local_data()


df = get_data()

# -- HANDLE EMPTY STATE --
if df.empty:
    st.warning("⚠️ No data found. Run the ingestion pipeline first:")
    st.code("python src/ingestion.py", language="bash")
    st.info("Or with Docker: `docker compose up ingestion`")
    st.stop()

# -- SIDEBAR FILTERS --
st.sidebar.header("🔧 Filters")
cities = ["All"] + sorted(df["city"].unique().tolist())
selected_city = st.sidebar.selectbox("Select City", cities)

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
filtered_df = df.copy()
if selected_city != "All":
    filtered_df = filtered_df[filtered_df["city"] == selected_city]
if len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df["date"] >= date_range[0]) & (filtered_df["date"] <= date_range[1])]

# -- SUMMARY METRICS --
metrics = get_summary_metrics(filtered_df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Total Records", f"{metrics['total_records']:,}")
col2.metric("🏙️ Cities", metrics["cities"])
col3.metric("✅ Data Quality", f"{metrics['quality_pct']}%")
col4.metric("📅 Date Range", metrics["date_range"])

# -- TEMPERATURE CHART --
st.subheader("🌡️ Temperature Trends")

daily_temp = filtered_df.groupby(["date", "city"])["temperature_c"].mean().reset_index()
fig_temp = px.line(
    daily_temp,
    x="date",
    y="temperature_c",
    color="city",
    labels={"temperature_c": "Avg Temperature (°C)", "date": "Date", "city": "City"},
    title="Daily Average Temperature by City",
)
st.plotly_chart(fig_temp, use_container_width=True)

# -- HUMIDITY & WIND CHARTS (side by side) --
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💧 Humidity")
    daily_humidity = filtered_df.groupby(["date", "city"])["humidity_pct"].mean().reset_index()
    fig_hum = px.line(
        daily_humidity,
        x="date",
        y="humidity_pct",
        color="city",
        labels={"humidity_pct": "Avg Humidity (%)", "date": "Date"},
    )
    st.plotly_chart(fig_hum, use_container_width=True)

with col_right:
    st.subheader("💨 Wind Speed")
    daily_wind = filtered_df.groupby(["date", "city"])["wind_speed_kmh"].mean().reset_index()
    fig_wind = px.line(
        daily_wind,
        x="date",
        y="wind_speed_kmh",
        color="city",
        labels={"wind_speed_kmh": "Avg Wind (km/h)", "date": "Date"},
    )
    st.plotly_chart(fig_wind, use_container_width=True)

# -- DATA QUALITY CHECKS --
st.subheader("🔍 Data Quality Checks")
quality_results = run_quality_checks(filtered_df)
st.dataframe(
    quality_results,
    column_config={
        "validation": "Validation Rule",
        "status": "Status",
        "detail": "Details",
    },
    use_container_width=True,
    hide_index=True,
)

# -- RAW DATA PREVIEW --
with st.expander("📋 View Raw Data Sample"):
    st.dataframe(filtered_df.head(100), use_container_width=True)

# -- FOOTER --
st.markdown("---")
st.markdown(
    "Built by [Andika Bhaskara](https://id.linkedin.com/in/mohamad-andika-bhaskara) "
    "| [GitHub](https://github.com/andikabhaskara/weather-data-quality-platform) "
    "| [Medium](https://medium.com/@AndikaBhas/about)"
)
