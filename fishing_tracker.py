import streamlit as st
import pandas as pd
import datetime
import requests

st.set_page_config(page_title="Fishing Conditions Tracker", layout="wide")

st.title("🎣 West Fork Fishing Conditions Tracker")

# Load or create a simple log
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Date", "Air Temp (°F)", "Weather", "Fly Used", "Fish Caught", "Notes"])

# Get current weather and recent rainfall for Azusa, CA using Open-Meteo
weather_api = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 34.1336,
    "longitude": -117.9076,
    "daily": ["precipitation_sum", "temperature_2m_max", "temperature_2m_min", "weathercode"],
    "timezone": "auto"
}
response = requests.get(weather_api, params=params)
weather_data = response.json() if response.status_code == 200 else None

# Map weather codes to conditions (simplified version)
weather_code_map = {
    0: "Sunny",
    1: "Partly Cloudy",
    2: "Overcast",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Rainy",
    53: "Rainy",
    55: "Rainy",
    61: "Rainy",
    63: "Rainy",
    65: "Rainy",
    80: "Rainy",
    81: "Rainy",
    82: "Rainy",
    95: "Windy",
    96: "Windy",
    99: "Windy"
}

# Show weather snapshot
if weather_data:
    st.subheader("🌦️ Current Conditions Snapshot (Azusa, CA)")
    today_index = 0
    today_precip = weather_data['daily']['precipitation_sum'][today_index]
    temp_max = weather_data['daily']['temperature_2m_max'][today_index]
    temp_min = weather_data['daily']['temperature_2m_min'][today_index]
    weather_code = weather_data['daily']['weathercode'][today_index]
    today_weather_condition = weather_code_map.get(weather_code, "Unknown")

    st.metric("Today's High Temp", f"{temp_max}°F")
    st.metric("Today's Low Temp", f"{temp_min}°F")
    st.metric("Precipitation (Today)", f"{today_precip} mm")
    st.markdown(f"**Condition:** {today_weather_condition}")

    # Predictive Insight: compare today's weather with logged trips
    if not st.session_state.log.empty:
        st.subheader("🔍 Recommendation Based on Past Trips")
        past_similar = st.session_state.log[
            (st.session_state.log["Air Temp (°F)"].between(temp_min, temp_max)) &
            (st.session_state.log["Weather"] == today_weather_condition)
        ]
        if not past_similar.empty:
            avg_catch = past_similar["Fish Caught"].mean()
            common_flies = past_similar["Fly Used"].mode().tolist()
            st.markdown(f"**🎯 Average Fish Caught on Similar Days:** {avg_catch:.2f}")
            if common_flies:
                st.markdown(f"**🪰 Flies That Worked:** {', '.join(common_flies)}")
            else:
                st.markdown("No consistent fly pattern from those trips.")
        else:
            st.markdown("No similar past conditions found in your log.")

# Trip logging form
with st.form("log_form"):
    st.subheader("📝 Log a Fishing Trip")
    date = st.date_input("Date", value=datetime.date.today())
    air_temp = st.number_input("Air Temperature (°F)", min_value=30, max_value=120, step=1)
    weather = st.selectbox("Weather", ["Sunny", "Partly Cloudy", "Overcast", "Rainy", "Windy"])
    fly = st.text_input("Fly Used")
    fish_caught = st.number_input("Fish Caught", min_value=0, step=1)
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add Trip")

    if submitted:
        new_row = pd.DataFrame({
            "Date": [date],
            "Air Temp (°F)": [air_temp],
            "Weather": [weather],
            "Fly Used": [fly],
            "Fish Caught": [fish_caught],
            "Notes": [notes]
        })
        st.session_state.log = pd.concat([st.session_state.log, new_row], ignore_index=True)
        st.success("Trip logged!")

# Show trip log
st.subheader("📅 Logged Trips")
st.dataframe(st.session_state.log.sort_values("Date", ascending=False))

# Basic analysis
if not st.session_state.log.empty:
    st.subheader("📊 Trends")
    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(st.session_state.log.groupby("Weather")["Fish Caught"].mean())

    with col2:
        st.line_chart(st.session_state.log.groupby("Date")["Fish Caught"].sum())
