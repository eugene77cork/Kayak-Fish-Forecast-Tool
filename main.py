import random
import json
import urllib.request
from datetime import datetime, timezone, timedelta
import os
import ssl

# Replace with your real OpenWeatherMap API keys
API_KEYS = [
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', #training
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
]

# Replace with your real weatherapi.com API keys
API_KEYS2 = [
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',#training
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
]

# Replace with your real stormglass API keys
API_KEYS3 = [
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',#training
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
]

KEY_CACHE_FILE = "api_key_cache.json"
KEY_CACHE_FILE2 = "api2_key_cache.json"
KEY_CACHE_FILE3 = "api3_key_cache.json"

WEATHER_ICONS = {
    "clear sky": "☀️",
    "few clouds": "🌤",
    "scattered clouds": "⛅",
    "broken clouds": "☁️",
    "overcast clouds": "☁️",
    "shower rain": "🌦",
    "rain": "🌧",
    "light rain": "🌧",
    "moderate rain": "🌧",
    "heavy intensity rain": "🌧",
    "very heavy rain": "🌧",
    "extreme rain": "🌧🌪️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "light snow": "🌨",
    "heavy snow": "❄️❄️❄️",
    "mist": "🌫️",
    "fog": "🌫️",
    "haze": "🌫️",
    "drizzle": "🌦",
    "default": "🌀"
}

MOON_PHASE_ICONS = {
    "New Moon": "🌑",
    "Waxing Crescent": "🌒",
    "First Quarter": "🌓",
    "Waxing Gibbous": "🌔",
    "Full Moon": "🌕",
    "Waning Gibbous": "🌖",
    "Last Quarter": "🌗",
    "Waning Crescent": "🌘"
}

def load_cached_keys():
    if not os.path.exists(KEY_CACHE_FILE):
        with open(KEY_CACHE_FILE, 'w') as f:
            json.dump({"active": API_KEYS, "cooldown": {}}, f)
    with open(KEY_CACHE_FILE, 'r') as f:
        return json.load(f)

def load_cached_keys2():
    if not os.path.exists(KEY_CACHE_FILE2):
        with open(KEY_CACHE_FILE2, 'w') as f:
            json.dump({"active": API_KEYS2, "cooldown": {}}, f)
    with open(KEY_CACHE_FILE2, 'r') as f:
        return json.load(f)

def load_cached_keys3():
    if not os.path.exists(KEY_CACHE_FILE3):
        with open(KEY_CACHE_FILE3, 'w') as f:
            json.dump({"active": API_KEYS3, "cooldown": {}}, f)
    with open(KEY_CACHE_FILE3, 'r') as f:
        return json.load(f)

def save_cached_keys(data):
    with open(KEY_CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_cached_keys2(data):
    with open(KEY_CACHE_FILE2, 'w') as f:
        json.dump(data, f, indent=2)

def save_cached_keys3(data):
    with open(KEY_CACHE_FILE3, 'w') as f:
        json.dump(data, f, indent=2)

def get_valid_api_key():
    data = load_cached_keys()
    now = datetime.now().timestamp()
    for key, cooldown_time in list(data["cooldown"].items()):
        if now >= cooldown_time:
            del data["cooldown"][key]
            data["active"].append(key)
    save_cached_keys(data)
    if not data["active"]:
        raise Exception("No valid API keys available.")
    return random.choice(data["active"])

def get_valid_api_key2():
    data = load_cached_keys2()
    now = datetime.now().timestamp()
    for key, cooldown_time in list(data["cooldown"].items()):
        if now >= cooldown_time:
            del data["cooldown"][key]
            data["active"].append(key)
    save_cached_keys2(data)
    if not data["active"]:
        raise Exception("No valid API keys available.")
    return random.choice(data["active"])

def get_valid_api_key3():
    data = load_cached_keys3()
    now = datetime.now().timestamp()
    for key, cooldown_time in list(data["cooldown"].items()):
        if now >= cooldown_time:
            del data["cooldown"][key]
            data["active"].append(key)
    save_cached_keys3(data)
    if not data["active"]:
        raise Exception("No valid API keys available.")
    return random.choice(data["active"])

def get_coords_from_city(city_input, max_retries=3):
    print(f"[INFO] Location chosen: {city_input}")
    print("[INFO] Fetching coordinates via Geocoding API...")

    for attempt in range(max_retries):
        try:
            api_key = get_valid_api_key()
            print(f"[DEBUG] Trying OpenWeather API key: {api_key[:8]}... (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ No valid OpenWeather API keys available.")
            return None, None

        base_url = "http://api.openweathermap.org/geo/1.0/direct"
        url = f"{base_url}?q={city_input}&limit=1&appid={api_key}"
        print(f"[INFO] Fetching GEOCODING API URL")

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))
            if data:
                lat = data[0]['lat']
                lon = data[0]['lon']
                print(f"[INFO] Coordinates found: lat={lat}, lon={lon}")
                return lat, lon
            else:
                print("❌ No results found for that location.")
                return None, None

        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("⚠️ [ERROR] API key rate limit exceeded. Removing key temporarily.")
                data = load_cached_keys()
                if api_key in data["active"]:
                    data["active"].remove(api_key)
                    cooldown_until = datetime.now().timestamp() + 86400
                    data["cooldown"][api_key] = cooldown_until
                    save_cached_keys(data)
                print("⏭️ Trying next key...")
                continue
            else:
                print(f"⚠️ [ERROR] HTTP {e.code}: {e.reason}")
                return None, None
        except Exception as e:
            print(f"⚠️ [ERROR] Failed to retrieve coordinates: {e}")
            return None, None

    print(f"❌ Gave up after {max_retries} attempts.")
    return None, None

def fetch_openweather_weather(lat, lon, units='metric', max_retries=3):
    print("[INFO] Fetching basic weather data from OpenWeatherMap...")

    for attempt in range(max_retries):
        try:
            api_key = get_valid_api_key()
            print(f"[DEBUG] Using OpenWeather key: {api_key[:8]}... (attempt {attempt + 1})")
        except Exception:
            print("❌ No working OpenWeather keys.")
            return {}

        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}"
        print(f"[INFO] Fetching OPENWEATHERMAP WEATHER URL")

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

            main = data.get("main", {})
            wind = data.get("wind", {})
            clouds = data.get("clouds", {})
            sys = data.get("sys", {})
            name = data.get("name", "Unknown Location")
            weather_list = data.get("weather", [{}])
            weather_desc = weather_list[0].get("description", "").lower()

            icon = next((icon for key, icon in WEATHER_ICONS.items() if key in weather_desc), WEATHER_ICONS["default"])

            dt = data.get("dt")
            tz_offset_sec = data.get("timezone", 0)
            try:
                obs_utc = datetime.fromtimestamp(dt, tz=timezone.utc)
                obs_local = obs_utc + timedelta(seconds=tz_offset_sec)
                obs_time_str = obs_local.strftime("%H:%M")
            except:
                obs_time_str = "N/A"

            sunrise_utc_raw = sys.get("sunrise")
            sunset_utc_raw = sys.get("sunset")
            try:
                sunrise_utc = datetime.fromtimestamp(sunrise_utc_raw, tz=timezone.utc)
                sunset_utc = datetime.fromtimestamp(sunset_utc_raw, tz=timezone.utc)
                sunrise_local = sunrise_utc + timedelta(seconds=tz_offset_sec)
                sunset_local = sunset_utc + timedelta(seconds=tz_offset_sec)
                sunrise_str = sunrise_local.strftime("%H:%M")
                sunset_str = sunset_local.strftime("%H:%M")
            except Exception as e:
                sunrise_str = "N/A"
                sunset_str = "N/A"

            pressure = main.get("pressure")
            if pressure is not None:
                if pressure > 1015: pressure_desc = "High"
                elif pressure < 1005: pressure_desc = "Low"
                else: pressure_desc = "Normal"
                pressure_str = f"{pressure} hPa ({pressure_desc})"
            else:
                pressure_str = "N/A"

            temp = main.get("temp")
            feels_like = main.get("feels_like")
            temp_str = round(temp) if temp is not None else "N/A"
            feels_like_str = round(feels_like) if feels_like is not None else "N/A"
            humidity = main.get("humidity")
            humidity_str = f"{humidity}%" if humidity is not None else "N/A"
            wind_speed = wind.get("speed")
            wind_gust = wind.get("gust")
            wind_speed_str = round(wind_speed, 1) if wind_speed is not None else "N/A"
            wind_gust_str = round(wind_gust, 1) if wind_gust is not None else "N/A"
            cloud_cover = clouds.get("all")
            cloud_str = f"{cloud_cover}%" if cloud_cover is not None else "N/A"
            visibility = data.get("visibility")
            visibility_str = f"{round(visibility / 1000, 1)} km" if visibility is not None else "N/A"

            result = {
                f"{icon}  Weather": weather_desc.title(),
                "📍  Weather Station ": name,
                "🕘  Time (Local)": obs_time_str,
                "🌡  Temperature (°C)": temp_str,
                "🔥  Feels Like (°C)": feels_like_str,
                "💧  Humidity (%)": humidity_str,
                "🌬  Wind Speed (m/s)": wind_speed_str,
                "💨  Wind Gust (m/s)": wind_gust_str,
                "🧭  Pressure": pressure_str,
                "☁️  Cloud Cover (%)": cloud_str,
                "🌅  Sunrise": sunrise_str,
                "🌇  Sunset": sunset_str,
                "👀  Visibility (km)": visibility_str
            }

            print("[INFO] Basic weather data received.")
            return result

        except urllib.error.HTTPError as e:
            if e.code == 429:
                data = load_cached_keys()
                if api_key in data["active"]:
                    data["active"].remove(api_key)
                    data["cooldown"][api_key] = datetime.now().timestamp() + 86400
                    save_cached_keys(data)
                print("⏭️ Rate limited. Trying next key...")
                continue
            else:
                print(f"⚠️ HTTP error {e.code}. Not retrying.")
                return {}
        except Exception as e:
            print(f"⚠️ [ERROR] Failed to retrieve OpenWeatherMap data: {e}")
            return {}

    return {}

def degrees_to_compass(deg):
    if deg is None:
        return "N/A"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((deg / 45) + 0.5) % 8
    return dirs[idx]

def fetch_marine_weather(lat, lon, max_retries=3):
    print("[INFO] Fetching marine weather data from Open-Meteo...")

    url = (
        f"http://marine-api.open-meteo.com/v1/marine?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=wave_height,swell_wave_height,wave_direction,sea_surface_temperature"
        "&current_weather=true"
    )
    print(f"[INFO] Fetching OPEN-METEO MARINE API URL")

    for _ in range(max_retries):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

            hourly = data.get("hourly", {})
            wave_height = hourly.get("wave_height", [None])[0]
            swell_height = hourly.get("swell_wave_height", [None])[0]
            wave_dir = hourly.get("wave_direction", [None])[0]
            sea_temp = hourly.get("sea_surface_temperature", [None])[0]

            wave_str = f"{round(float(wave_height), 2)} m" if wave_height is not None else "N/A"
            swell_str = f"{round(float(swell_height), 2)} m" if swell_height is not None else "N/A"
            wave_dir_deg = round(float(wave_dir), 1) if wave_dir is not None else "N/A"
            wave_dir_txt = degrees_to_compass(wave_dir) if wave_dir is not None else ""
            wave_dir_full = f"{wave_dir_deg}° ({wave_dir_txt})" if wave_dir_deg != "N/A" else "N/A"
            sea_temp_str = f"{round(float(sea_temp), 1)}°C" if sea_temp is not None else "N/A"

            result = {
                "🌊  Wave Height": wave_str,
                "🌀  Swell Height": swell_str,
                "🧭  Wave Direction": wave_dir_full,
                "🌡  Sea Surface Temp": sea_temp_str
            }
            print("[INFO] Marine weather data received.")
            return result

        except Exception as e:
            print(f"⚠️ [ERROR] Failed to retrieve marine weather data: {e}")
            # Open-Meteo is free — no key rotation needed; just retry
            continue

    return {}

def fetch_fishing_behavior(location, max_retries=3):
    print("[INFO] Fetching moon phase and fishing conditions...")

    for attempt in range(max_retries):
        try:
            api_key2 = get_valid_api_key2()
            print(f"[DEBUG] Using WeatherAPI key: {api_key2[:8]}... (attempt {attempt + 1})")
        except Exception:
            print("❌ No valid WeatherAPI keys.")
            return {}

        date_today = datetime.now().strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/astronomy.json?key={api_key2}&q={location}&dt={date_today}"
        print(f"[INFO] Fetching WEATHERAPI ASTRONOMY URL")

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

            astro = data.get("astronomy", {}).get("astro", {})
            moon_phase = astro.get("moon_phase", "N/A")
            moon_icon = MOON_PHASE_ICONS.get(moon_phase, "🌙")
            illumination = astro.get("moon_illumination", "N/A")
            try:
                illumination = int(illumination)
            except:
                illumination = 0

            if moon_phase in ["New Moon", "Full Moon"]:
                behavior = "🌟🌟🌟🌟 (High) – Excellent time to fish!"
            elif moon_phase in ["First Quarter", "Last Quarter"]:
                behavior = "🌟🌟🌟 (Moderate–Good) – Decent activity"
            elif illumination > 75:
                behavior = "🌟🌟🌟 (Moderate–Good) – Bright moon boosts feeding"
            elif illumination < 25:
                behavior = "🌟🌟 (Low–Moderate) – Lower activity, try dawn/dusk"
            else:
                behavior = "🌟🌟🌟 (Average) – Varies with conditions"

            sunrise = astro.get("sunrise", "N/A")
            sunset = astro.get("sunset", "N/A")
            moonrise = astro.get("moonrise", "N/A")
            moonset = astro.get("moonset", "N/A")

            best_times = []
            if sunrise != "N/A": best_times.append(f"🌅 Sunrise: {sunrise}")
            if sunset != "N/A": best_times.append(f"🌇 Sunset: {sunset}")
            if moonrise != "N/A": best_times.append(f"🌙 Moonrise: {moonrise}")
            if moonset != "N/A": best_times.append(f"🌘 Moonset: {moonset}")

            today_str = datetime.now().strftime("%A, %B %d, %Y")

            result = {
                "📅 Fishing Forecast": today_str,
                f"{moon_icon} Moon Phase": f"{moon_phase} ({illumination}% illuminated)",
                "📈 Activity Level": behavior,
                "⏰ Best Times to Fish": " | or | ".join(best_times) if best_times else "N/A"
            }

            print("[INFO] Fishing behavior data received.")
            return result

        except urllib.error.HTTPError as e:
            if e.code == 429:
                data = load_cached_keys2()
                if api_key2 in data["active"]:
                    data["active"].remove(api_key2)
                    data["cooldown"][api_key2] = datetime.now().timestamp() + 86400
                    save_cached_keys2(data)
                print("⏭️ Rate limited. Trying next key...")
                continue
            else:
                print(f"⚠️ HTTP error {e.code}. Not retrying.")
                return {}
        except Exception as e:
            print(f"⚠️ [ERROR] Failed to retrieve moon/fishing data: {e}")
            return {}

    return {}

def fetch_tide_data(lat, lon, max_retries=3):
    print("[INFO] Fetching tide data from StormGlass...")

    for attempt in range(max_retries):
        try:
            api_key3 = get_valid_api_key3()
            print(f"[DEBUG] Using StormGlass key: {api_key3[:8]}... (attempt {attempt + 1})")
        except Exception:
            print("❌ No valid StormGlass keys.")
            return []

        base_url = "https://api.stormglass.io/v2/tide/extremes/point"
        start_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        end_time = (datetime.now(timezone.utc) + timedelta(hours=48)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        params = urllib.parse.urlencode({
            "lat": lat,
            "lng": lon,
            "start": start_time,
            "end": end_time
        })
        url = f"{base_url}?{params}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", api_key3)

        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data.get("data", [])
                else:
                    print(f"[ERROR] StormGlass returned HTTP {response.status}")
                    return []

        except urllib.error.HTTPError as e:
            if e.code == 402:
                print("[ERROR] StormGlass key reached daily limit. Marking for cooldown.")
                data = load_cached_keys3()
                if api_key3 in data["active"]:
                    data["active"].remove(api_key3)
                    data["cooldown"][api_key3] = datetime.now().timestamp() + 86400
                    save_cached_keys3(data)
                print("⏭️ Trying next key...")
                continue
            else:
                print(f"[ERROR] Failed to retrieve tide data: {e.reason}")
                return []
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching tide data: {e}")
            return []

    return []

def print_tide_data(tide_list):
    print("\n🌊 Tides Forecast for next 24 hours")
    print("-" * 60)
    if not tide_list:
        print("⛵ No valid tide predictions available.")
        print("-" * 60)
        return
    for entry in tide_list[:6]:
        time_str = entry.get("time", "N/A")
        tide_type = entry.get("type", "unknown").lower()
        height = entry.get("height", "N/A")
        try:
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            time_only = dt.strftime("%H:%M")
            day_name = dt.strftime("%A")
        except Exception as e:
            time_only = "N/A"
            day_name = ""
        if tide_type == "high":
            icon = "📈"
            label = "High Tide"
        elif tide_type == "low":
            icon = "📉"
            label = "Low Tide"
        else:
            icon = "⛵"
            label = "Tide"
        if time_only != "N/A":
            line = f"{icon} {label:<10} {time_only} ({day_name}) : {height:.2f} m"
        else:
            line = f"{icon} {label} – {height:.2f} m"
        print(line)
    print("-" * 60)

def print_weather_report(weather_data):
    print("\n🌤️  Weather Report")
    print("-" * 40)
    for key, value in weather_data.items():
        print(f"{key + ':':<20} {value}")
    print("-" * 40)

def print_marine_weather(marine_data):
    print("\n🌊  Marine Weather Report for Kayaking & Fishing 🛶🎣")
    print("-" * 50)
    for key, value in marine_data.items():
        print(f"{key + ':':<25} {value}")
    print("-" * 50)

def print_fishing_behavior(fishing_data):
    forecast = fishing_data.get("📅 Fishing Forecast", "Unknown Date")
    print(f"\n🎣  Fishing Forecast ({forecast})")
    print("-" * 60)
    KEY_WIDTH = 24
    for key, value in fishing_data.items():
        if key == "📅 Fishing Forecast":
            continue
        lines = value.split('\n') if '\n' in value else [value]
        print(f"{key.ljust(KEY_WIDTH)} {lines[0]}")
        for line in lines[1:]:
            print(f"{''.ljust(KEY_WIDTH)} {line}")
    print("-" * 60)

if __name__ == "__main__":
    print("🌍 Welcome to Kayak & Fish Forecast Tool!")
    location = input("📍 Enter location (e.g., Kinsale,IE): ").strip()

    lat, lon = get_coords_from_city(location)

    if lat is not None and lon is not None:
        weather_data = fetch_openweather_weather(lat, lon)
        marine_data = fetch_marine_weather(lat, lon)
        fishing_report = fetch_fishing_behavior(location)
        tide_data = fetch_tide_data(lat, lon)

        if weather_data:
            print_weather_report(weather_data)
        if marine_data:
            print_marine_weather(marine_data)
        if fishing_report:
            print_fishing_behavior(fishing_report)
        if tide_data:
            print_tide_data(tide_data)
        else:
            print("\n⛵ No tide predictions available.")
            print("-" * 50)
    else:
        print("❌ Unable to fetch weather due to invalid location.")
