import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objs as go
import pandas as pd

# -------- Helper functions --------

def classify_conditions(temp_f, wind_mph, precip_mm):
    labels = []
    if temp_f >= 90:
        labels.append("Very Hot")
    elif temp_f >= 75:
        labels.append("Hot")
    elif temp_f <= 32:
        labels.append("Very Cold")
    elif temp_f <= 45:
        labels.append("Cold")
    if wind_mph >= 20:
        labels.append("Very Windy")
    if precip_mm >= 10:
        labels.append("Very Wet")
    if not labels:
        labels.append("Comfortable")
    return labels

def get_daily_data(lat, lon, month, day, start_year, end_year):
    records = []
    for year in range(start_year, end_year + 1):
        date_str = f"{year}{month:02d}{day:02d}"
        url = (
            f"https://power.larc.nasa.gov/api/temporal/daily/point"
            f"?parameters=T2M,WS10M,PRECTOTCORR"
            f"&community=RE&longitude={lon}&latitude={lat}"
            f"&start={date_str}&end={date_str}&format=JSON"
        )
        r = requests.get(url)
        if r.status_code != 200:
            continue
        data = r.json()
        try:
            t_c = data["properties"]["parameter"]["T2M"][date_str]
            w_ms = data["properties"]["parameter"]["WS10M"][date_str]
            p_mm = data["properties"]["parameter"]["PRECTOTCORR"][date_str]
            t_f = t_c * 9 / 5 + 32
            w_mph = w_ms * 2.23694
            records.append({
                "year": year,
                "temp_f": t_f,
                "wind_mph": w_mph,
                "precip_mm": p_mm,
                "labels": classify_conditions(t_f, w_mph, p_mm)
            })
        except Exception:
            continue
    return records

def summarize(records, lat, lon, month, day, year):
    n = len(records)
    avg_temp = sum(r["temp_f"] for r in records) / n
    avg_wind = sum(r["wind_mph"] for r in records) / n
    avg_precip = sum(r["precip_mm"] for r in records) / n

    very_cold_count = sum(r["temp_f"] < 35 for r in records)
    cold_count = sum(35 <= r["temp_f"] <= 60 for r in records)
    hot_count = sum(61 <= r["temp_f"] <= 80 for r in records)
    very_hot_count = sum(r["temp_f"] > 80 for r in records)
    very_windy_count = sum('Very Windy' in r["labels"] for r in records)
    very_wet_count = sum('Very Wet' in r["labels"] for r in records)

    chances = {
        "very cold": very_cold_count / n * 100,
        "moderately cold": cold_count / n * 100,
        "hot": hot_count / n * 100,
        "very hot": very_hot_count / n * 100,
        "very windy": very_windy_count / n * 100,
        "very wet": very_wet_count / n * 100,
    }

    # Bulleted averages
    result_lines = []

    # Swap positions: First Predicted Conditions header (with bulleted chances)
    result_lines.append("### Predicted Conditions\n")
    significant = {k: v for k, v in chances.items() if v > 50}
    if significant:
        for condition, chance in significant.items():
            result_lines.append(f"- Chances of being {condition}: {chance:.1f}%")
    else:
        top_cond = max(chances, key=chances.get)
        result_lines.append(f"- Most likely condition: {top_cond} ({chances[top_cond]:.1f}%)")

    # Then Summary header with averages
    result_lines.append(f"\n### 40-year historical weather summary for {year}-{month:02d}-{day:02d} at ({lat}, {lon})\n")
    result_lines.append(f"- **Average Temperature:** {avg_temp:.1f}°F")
    result_lines.append(f"- **Average Wind Speed:** {avg_wind:.1f} mph")
    result_lines.append(f"- **Average Precipitation:** {avg_precip:.1f} mm")

    return "\n\n".join(result_lines), avg_temp, avg_wind, avg_precip

def plot_time_series(records, avg_temp, avg_wind, avg_precip):
    years = [r["year"] for r in records]
    temps = [r["temp_f"] for r in records]
    winds = [r["wind_mph"] for r in records]
    precips = [r["precip_mm"] for r in records]

    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=years, y=temps, mode='lines+markers', name='Temperature (°F)', line_shape='spline'))
    temp_fig.add_trace(go.Scatter(x=years, y=[avg_temp]*len(years), mode='lines', name='Avg Temp', line=dict(dash='dash', color='yellow')))
    temp_fig.update_layout(title='Temperature over Years', height=350)

    wind_fig = go.Figure()
    wind_fig.add_trace(go.Scatter(x=years, y=winds, mode='lines+markers', name='Wind Speed (mph)', line_shape='spline'))
    wind_fig.add_trace(go.Scatter(x=years, y=[avg_wind]*len(years), mode='lines', name='Avg Wind', line=dict(dash='dash', color='yellow')))
    wind_fig.update_layout(title='Wind Speed over Years', height=350)

    precip_fig = go.Figure()
    precip_fig.add_trace(go.Scatter(x=years, y=precips, mode='lines+markers', name='Precipitation (mm)', line_shape='spline'))
    precip_fig.add_trace(go.Scatter(x=years, y=[avg_precip]*len(years), mode='lines', name='Avg Precip', line=dict(dash='dash', color='yellow')))
    precip_fig.update_layout(title='Precipitation over Years', height=350)

    return temp_fig, wind_fig, precip_fig

# -------- Streamlit App --------

st.set_page_config(page_title="Outdoor Weather Predictor", layout="wide")

# Black background with white text
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center; color:white;'>ClimaCast</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>Enter latitude, longitude, and date to see historical weather patterns and predicted outdoor comfort levels.</p>", unsafe_allow_html=True)

with st.sidebar:
    lat_str = st.text_input("Latitude", value="0", placeholder="Enter latitude")
    lon_str = st.text_input("Longitude", value="0", placeholder="Enter longitude")
    date_input = st.date_input("Date", value=datetime(2025, 1, 1))

if st.button("Get weather information"):
    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except ValueError:
        st.error("Please enter valid numeric latitude and longitude.")
        st.stop()

    dt = date_input
    year, month, day = dt.year, dt.month, dt.day
    start_year = year - 40
    end_year = year - 1

    with st.spinner("Fetching and processing NASA POWER data..."):
        data_records = get_daily_data(lat, lon, month, day, start_year, end_year)

    if not data_records:
        st.error("No data found for this location and date range. Try different input.")
    else:
        summary_md, avg_temp, avg_wind, avg_precip = summarize(data_records, lat, lon, month, day, year)
        st.markdown(summary_md)

        plotly_config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "sendDataToCloud", "pan2d", "select2d", "lasso2d",
                "autoScale2d", "resetScale2d", "hoverClosestCartesian",
                "hoverCompareCartesian", "toggleSpikelines", "toImage"
            ]
        }

        col1, col2, col3 = st.columns(3)
        temp_fig, wind_fig, precip_fig = plot_time_series(data_records, avg_temp, avg_wind, avg_precip)

        with col1:
            st.plotly_chart(temp_fig, use_container_width=True, config=plotly_config)
        with col2:
            st.plotly_chart(wind_fig, use_container_width=True, config=plotly_config)
        with col3:
            st.plotly_chart(precip_fig, use_container_width=True, config=plotly_config)

        csv = pd.DataFrame(data_records).drop(columns="labels").to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"weather_history_{lat}_{lon}_{month:02d}{day:02d}.csv",
            mime="text/csv"
        )
