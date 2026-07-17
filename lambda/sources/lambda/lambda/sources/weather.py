"""
Weather data fetcher using OpenWeatherMap API.
"""
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger()


def fetch_weather(city: str, api_key: str) -> dict:
    """
    Fetch current weather and forecast for a city.
    """
    try:
        params = urllib.parse.urlencode({
            "q": city,
            "appid": api_key,
            "units": "imperial"
        })
        url = f"https://api.openweathermap.org/data/2.5/weather?{params}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            current = json.loads(response.read().decode())
        
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?{params}&cnt=8"
        req = urllib.request.Request(forecast_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            forecast = json.loads(response.read().decode())
        
        temps = [item["main"]["temp"] for item in forecast.get("list", [])]
        high = max(temps) if temps else current["main"]["temp_max"]
        low = min(temps) if temps else current["main"]["temp_min"]
        
        return {
            "city": city,
            "temperature": round(current["main"]["temp"]),
            "feels_like": round(current["main"]["feels_like"]),
            "high": round(high),
            "low": round(low),
            "description": current["weather"][0]["description"],
            "humidity": current["main"]["humidity"],
            "wind_speed": round(current["wind"]["speed"]),
        }
        
    except Exception as e:
        logger.warning("Weather fetch failed: %s", str(e))
        return {
            "city": city,
            "error": str(e),
            "temperature": None,
            "description": "unavailable"
        }
