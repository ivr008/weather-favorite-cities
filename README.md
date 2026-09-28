# Weather in My Favorite Cities 🌤️

A simple [Streamlit](https://streamlit.io) app where you type in your 4 favorite
cities and see the current weather for each one.

## Features

- ✏️ Type any 4 cities (name, or "City, Country")
- 🌡️ Live weather via the free [Open-Meteo](https://open-meteo.com/) API (no key needed)
- 📍 Auto-resolves city names to real locations
- 🃏 Cards showing temperature, feels-like, humidity, wind, and conditions

## Run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the app
streamlit run app.py
```

## Deploy (optional)

You can host it for free on [Streamlit Community Cloud](https://share.streamlit.io):
just connect this GitHub repo and set the main file to `app.py`.
