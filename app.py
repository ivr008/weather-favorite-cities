import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="My Favorite Cities", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather in My Favorite Cities")
st.caption("Type in your 4 favorite cities and get the current weather.")

# ---------------------------------------------------------------------------
# Weather helpers
# ---------------------------------------------------------------------------
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Freezing drizzle (light)",
    57: "Freezing drizzle (dense)",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain (light)",
    67: "Freezing rain (heavy)",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(city: str) -> dict | None:
    """Resolve a city name and return current weather via Open-Meteo."""
    try:
        # 1) Geocode the city name
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        ).json()
        results = geo.get("results") or []
        if not results:
            return None

        place = results[0]
        name = place.get("name", city)
        country = place.get("country", "")
        admin = place.get("admin1", "")
        lat, lon = place["latitude"], place["longitude"]

        # 2) Fetch current weather
        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": ",".join(
                    [
                        "temperature_2m",
                        "apparent_temperature",
                        "relative_humidity_2m",
                        "weather_code",
                        "wind_speed_10m",
                    ]
                ),
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto",
            },
            timeout=10,
        ).json()
        cur = weather.get("current") or {}
        code = cur.get("weather_code", 0)

        return {
            "name": name,
            "country": country,
            "admin": admin,
            "lat": lat,
            "lon": lon,
            "temp_f": cur.get("temperature_2m"),
            "feels_f": cur.get("apparent_temperature"),
            "humidity": cur.get("relative_humidity_2m"),
            "wind_mph": cur.get("wind_speed_10m"),
            "description": WMO_CODES.get(code, "Unknown"),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Inputs: 4 favorite cities
# ---------------------------------------------------------------------------
with st.form("cities_form"):
    st.subheader("✏️ Your 4 favorite cities")
    col1, col2 = st.columns(2)
    with col1:
        city1 = st.text_input("City 1", value="Guaynabo, PR")
        city2 = st.text_input("City 2", value="Tokyo, Japan")
    with col2:
        city3 = st.text_input("City 3", value="Paris, France")
        city4 = st.text_input("City 4", value="Sydney, Australia")

    submitted = st.form_submit_button("Get Weather", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if submitted:
    cities = [city1, city2, city3, city4]
    cities = [c.strip() for c in cities if c.strip()]

    if not cities:
        st.warning("Please enter at least one city.")
        st.stop()

    with st.spinner("Fetching weather..."):
        results = [get_weather(c) for c in cities]

    cols = st.columns(len(cities))

    for col, city, data in zip(cols, cities, results):
        with col:
            if data is None:
                st.error(f"Could not find weather for **{city}**.")
                continue

            st.subheader(f"📍 {data['name']}")
            st.caption(f"{data['admin']}, {data['country']}".strip(", "))

            st.metric("Temperature", f"{data['temp_f']:.0f}°F")
            st.markdown(f"**{data['description']}**")

            details = pd.DataFrame(
                {
                    "Feels like": [f"{data['feels_f']:.0f}°F"],
                    "Humidity": [f"{data['humidity']:.0f}%"],
                    "Wind": [f"{data['wind_mph']:.0f} mph"],
                }
            )
            st.table(details)
