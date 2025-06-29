#!/usr/bin/env python3
"""
Test GROQ query understanding + free airport lookup
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

def understand_query(user_query):
    """Use GROQ to understand the flight query"""
    if not GROQ_API_KEY:
        print("❌ GROQ API key not available")
        return {}
    
    prompt = f"""
    Analyze this flight search query and extract the following information in JSON format:
    Query: "{user_query}"
    
    Extract:
    - origin_city: The departure city/location
    - destination_city: The arrival city/location  
    - departure_date: Departure date (YYYY-MM-DD format)
    - return_date: Return date if roundtrip (YYYY-MM-DD format, null if one-way)
    - passengers: Number of passengers (default 1)
    - max_price: Maximum price in USD (null if not specified)
    - trip_type: "roundtrip" or "one-way"
    
    Return only valid JSON, no other text.
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                parsed = json.loads(content)
                return parsed
            except json.JSONDecodeError:
                print(f"Failed to parse GROQ response: {content}")
                return {}
        else:
            print(f"GROQ API error: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"Error calling GROQ API: {e}")
        return {}

def geocode_city(city_name):
    """Geocode a city using OpenStreetMap"""
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
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                location = data[0]
                return {
                    "lat": float(location["lat"]),
                    "lon": float(location["lon"]),
                    "display_name": location["display_name"]
                }
        return None
            
    except Exception as e:
        print(f"Error geocoding {city_name}: {e}")
        return None

def main():
    test_queries = [
        "I want to fly from San Francisco to New York on July 15th, 2025 for under $500",
        "Roundtrip flights from Los Angeles to Chicago on August 10-15, 2025, 2 passengers"
    ]
    
    print("=== GROQ + Airport Lookup Test ===\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        print("-" * 50)
        
        # Step 1: Understand query with GROQ
        query_info = understand_query(query)
        if not query_info:
            print("❌ Failed to understand query")
            continue
        
        print("✅ Query understood:")
        print(f"   From: {query_info.get('origin_city')}")
        print(f"   To: {query_info.get('destination_city')}")
        print(f"   Date: {query_info.get('departure_date')}")
        if query_info.get('return_date'):
            print(f"   Return: {query_info.get('return_date')}")
        print(f"   Passengers: {query_info.get('passengers', 1)}")
        if query_info.get('max_price'):
            print(f"   Max Price: ${query_info.get('max_price')}")
        
        # Step 2: Geocode cities
        origin_city = query_info.get('origin_city')
        dest_city = query_info.get('destination_city')
        
        if origin_city:
            origin_coords = geocode_city(origin_city)
            if origin_coords:
                print(f"✅ {origin_city} geocoded: {origin_coords['lat']:.4f}, {origin_coords['lon']:.4f}")
            else:
                print(f"❌ Could not geocode {origin_city}")
        
        if dest_city:
            dest_coords = geocode_city(dest_city)
            if dest_coords:
                print(f"✅ {dest_city} geocoded: {dest_coords['lat']:.4f}, {dest_coords['lon']:.4f}")
            else:
                print(f"❌ Could not geocode {dest_city}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main() 