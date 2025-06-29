#!/usr/bin/env python3
"""
Simple test for geocoding using OpenStreetMap Nominatim
"""

import requests
import json

def geocode_city(city_name):
    """Test geocoding a city using OpenStreetMap"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }
        
        headers = {
            "User-Agent": "FlightAgent/1.0"
        }
        
        print(f"Geocoding: {city_name}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                location = data[0]
                print(f"✅ Found: {location['display_name']}")
                print(f"   Lat: {location['lat']}")
                print(f"   Lon: {location['lon']}")
                return {
                    "lat": float(location["lat"]),
                    "lon": float(location["lon"]),
                    "display_name": location["display_name"]
                }
            else:
                print(f"❌ No coordinates found for {city_name}")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    test_cities = [
        "San Francisco",
        "New York", 
        "Los Angeles",
        "Chicago",
        "Dallas"
    ]
    
    print("=== Geocoding Test ===\n")
    
    for city in test_cities:
        result = geocode_city(city)
        print()

if __name__ == "__main__":
    main() 