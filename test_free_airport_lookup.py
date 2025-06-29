#!/usr/bin/env python3
"""
Test script for the Free Airport Lookup
Tests geocoding and airport finding using free APIs.
"""

import sys
import os
sys.path.append('code')

from agents.free_airport_lookup import FreeAirportLookup

def main():
    # Initialize the free airport lookup
    lookup = FreeAirportLookup()
    
    # Test cities
    test_cities = [
        "San Francisco",
        "New York",
        "Los Angeles", 
        "Chicago",
        "Dallas",
        "Miami",
        "Seattle",
        "Las Vegas"
    ]
    
    print("=== Free Airport Lookup Test ===\n")
    
    for city in test_cities:
        print(f"Looking up airport for: {city}")
        print("-" * 40)
        
        try:
            # Get detailed airport info
            airport_info = lookup.get_airport_info(city)
            
            if airport_info:
                coords = airport_info["coordinates"]
                airport = airport_info["airport"]
                
                print(f"Found airport!")
                print(f"   City: {city}")
                print(f"   Coordinates: {coords['lat']:.4f}, {coords['lon']:.4f}")
                print(f"   Airport: {airport['name']}")
                print(f"   IATA Code: {airport['iata_code']}")
                try:
                    distance = float(airport['distance_km'])
                    print(f"   Distance: {distance:.1f} km")
                except Exception:
                    print(f"   Distance: {airport['distance_km']} km")
                print(f"   Country: {airport['country']}")
            else:
                print(f"❌ No airport found for {city}")
                
        except Exception as e:
            print(f"❌ Error looking up {city}: {e}")
        
        print()

if __name__ == "__main__":
    main() 