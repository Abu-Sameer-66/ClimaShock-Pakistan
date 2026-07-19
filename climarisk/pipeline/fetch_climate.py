import requests
import pandas as pd
import time
import json
from pathlib import Path

# cities jo hum cover kar rahe hain
# yahi 10 cities ClimaShock mein bhi hain — consistency ke liye same rakhna
PAKISTAN_CITIES = {
    "Karachi":    {"lat": 24.8607, "lon": 67.0011},
    "Lahore":     {"lat": 31.5204, "lon": 74.3587},
    "Faisalabad": {"lat": 31.4504, "lon": 73.1350},
    "Islamabad":  {"lat": 33.6844, "lon": 73.0479},
    "Multan":     {"lat": 30.1575, "lon": 71.5249},
    "Peshawar":   {"lat": 34.0151, "lon": 71.5805},
    "Quetta":     {"lat": 30.1798, "lon": 66.9750},
    "Sialkot":    {"lat": 32.4945, "lon": 74.5229},
    "Hyderabad":  {"lat": 25.3960, "lon": 68.3578},
    "Sukkur":     {"lat": 27.7052, "lon": 68.8574},
}

# yeh variables NASA ke official parameter codes hain
# T2M = temperature at 2 meters height (surface level)
# PRECTOTCORR = rainfall corrected for bias
# RH2M = relative humidity — water stress ke liye zaroori
# WS10M = wind speed — storm risk ke liye
NASA_PARAMS = "T2M,PRECTOTCORR,RH2M,WS10M"

# 1984 se start isliye ke NASA POWER ka reliable data yahin se hai
START_YEAR = "19840101"
END_YEAR   = "20231231"

# output folder — data/raw/climate mein save hoga
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw" / "climate"


def fetch_city_data(city_name, lat, lon):
    """
    ek city ke liye NASA POWER API call karta hai
    success pe DataFrame return karta hai
    failure pe None — taake loop continue kare
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    params = {
        "parameters": NASA_PARAMS,
        "community":  "RE",        # renewable energy community — best daily data
        "longitude":  lon,
        "latitude":   lat,
        "start":      START_YEAR,
        "end":        END_YEAR,
        "format":     "JSON",
    }

    try:
        print(f"  fetching {city_name} ({lat}, {lon})...")
        response = requests.get(url, params=params, timeout=60)

        # 200 matlab success — koi bhi aur code matlab problem
        if response.status_code != 200:
            print(f"  ERROR {city_name}: HTTP {response.status_code}")
            return None

        raw = response.json()

        # NASA ka response structure: data -> properties -> parameter -> {date: value}
        parameters = raw["properties"]["parameter"]

        # har parameter ek dict hai: {"19840101": 25.3, "19840102": 26.1, ...}
        # inhe ek DataFrame mein combine karte hain
        df = pd.DataFrame(parameters)
        df.index = pd.to_datetime(df.index, format="%Y%m%d")
        df.index.name = "date"

        # columns rename — NASA codes se readable names
        df.rename(columns={
            "T2M":          "temp_c",
            "PRECTOTCORR":  "rainfall_mm",
            "RH2M":         "humidity_pct",
            "WS10M":        "wind_ms",
        }, inplace=True)

        # city info add karo — baad mein merge karne ke liye zaroori
        df["city"] = city_name
        df["lat"]  = lat
        df["lon"]  = lon

        print(f"  OK {city_name}: {len(df)} days of data")
        return df

    except requests.exceptions.Timeout:
        print(f"  TIMEOUT {city_name} — skipping")
        return None
    except Exception as e:
        print(f"  FAILED {city_name}: {e}")
        return None


def fetch_all_cities():
    """
    sab cities ka data fetch karta hai
    har city ka alag CSV save karta hai
    end mein combined CSV bhi
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_data   = []
    successful = []
    failed     = []

    print(f"\nClimaRisk — NASA POWER Data Fetch")
    print(f"Cities: {len(PAKISTAN_CITIES)}")
    print(f"Period: {START_YEAR} to {END_YEAR}")
    print(f"Output: {OUTPUT_DIR}\n")

    for city_name, coords in PAKISTAN_CITIES.items():
        df = fetch_city_data(city_name, coords["lat"], coords["lon"])

        if df is not None:
            # individual city CSV — agar combined fail ho toh bhi data safe
            city_file = OUTPUT_DIR / f"{city_name.lower()}_climate.csv"
            df.to_csv(city_file)
            print(f"  saved → {city_file.name}")

            all_data.append(df)
            successful.append(city_name)
        else:
            failed.append(city_name)

        # NASA API pe polite rehna — 1 second gap per request
        time.sleep(1)

    # combined file — sab cities ek jagah
    if all_data:
        combined = pd.concat(all_data)
        combined_file = OUTPUT_DIR / "all_cities_climate.csv"
        combined.to_csv(combined_file)
        print(f"\ncombined saved → {combined_file.name}")

    # summary
    print(f"\n--- fetch complete ---")
    print(f"successful : {len(successful)} → {successful}")
    print(f"failed     : {len(failed)}     → {failed}")
    print(f"total rows : {len(combined) if all_data else 0}")

    return combined if all_data else None


if __name__ == "__main__":
    data = fetch_all_cities()

    if data is not None:
        print(f"\nsample — first 5 rows:")
        print(data.head())
        print(f"\ndate range: {data.index.min()} to {data.index.max()}")
        print(f"cities: {data['city'].unique()}")