import requests
import json
import logging
from typing import Optional, Dict, List
from dotenv import load_dotenv
import os
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('free_airport_lookup')

# Load environment variables
load_dotenv()
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME")  # You'll need to add this to your .env

AIRPORTS_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../airports.csv')

class FreeAirportLookup:
    def __init__(self):
        self.geonames_username = GEONAMES_USERNAME
        if not self.geonames_username:
            logger.warning("GEONAMES_USERNAME is not set. You can get a free username at http://www.geonames.org/login")
        self.airports_data = None

    def _load_airports_csv(self):
        if self.airports_data is not None:
            return
        self.airports_data = []
        try:
            with open(AIRPORTS_CSV_PATH, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.airports_data.append(row)
            logger.info(f"Loaded {len(self.airports_data)} airports from airports.csv")
        except Exception as e:
            logger.error(f"Error loading airports.csv: {e}")

    def _find_iata_in_csv(self, airport_name: str, city: Optional[str] = None) -> Optional[str]:
        self._load_airports_csv()
        if not self.airports_data:
            return None
        # Try exact match on airport name
        for row in self.airports_data:
            if row['name'].lower() == airport_name.lower() and row['iata_code']:
                return row['iata_code']
        # Try partial match on airport name
        for row in self.airports_data:
            if airport_name.lower() in row['name'].lower() and row['iata_code']:
                return row['iata_code']
        # Try match on city/municipality
        if city:
            for row in self.airports_data:
                if row['municipality'] and city.lower() in row['municipality'].lower() and row['iata_code']:
                    return row['iata_code']
        return None

    def geocode_city(self, city_name: str) -> Optional[Dict]:
        """
        Use OpenStreetMap Nominatim to geocode a city name to coordinates.
        """
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": city_name,
                "format": "json",
                "limit": 1
            }
            
            headers = {
                "User-Agent": "FlightAgent/1.0"  # Required by Nominatim
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
                else:
                    logger.warning(f"No coordinates found for {city_name}")
                    return None
            else:
                logger.error(f"Geocoding error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error geocoding {city_name}: {e}")
            return None

    def find_nearby_airports(self, lat: float, lon: float, radius_km: int = 50) -> List[Dict]:
        """
        Use GeoNames to find airports near the given coordinates.
        """
        if not self.geonames_username:
            logger.error("GeoNames username not available")
            return []
        
        try:
            url = "https://secure.geonames.org/findNearbyJSON"
            params = {
                "lat": lat,
                "lng": lon,
                "featureClass": "S",  # S = spot, building, farm
                "featureCode": "AIRP",  # AIRP = airport
                "radius": radius_km,
                "maxRows": 10,
                "username": self.geonames_username
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            print(f"[DEBUG] Raw GeoNames response: {response.text}")
            if response.status_code == 200:
                data = response.json()
                
                if 'geonames' in data:
                    airports = []
                    for airport in data['geonames']:
                        # Extract IATA code from alternate names if available
                        iata_code = self._extract_iata_code(airport)
                        
                        airports.append({
                            "name": airport.get("name", ""),
                            "iata_code": iata_code,
                            "distance_km": airport.get("distance", 0),
                            "country": airport.get("countryName", ""),
                            "lat": airport.get("lat", 0),
                            "lng": airport.get("lng", 0)
                        })
                    
                    # Sort by distance
                    airports.sort(key=lambda x: x["distance_km"])
                    return airports
                else:
                    logger.warning("No airports found in GeoNames response")
                    return []
            else:
                logger.error(f"GeoNames API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error finding nearby airports: {e}")
            return []

    def _extract_iata_code(self, airport: Dict) -> Optional[str]:
        """
        Extract IATA code from airport data.
        """
        # Check if IATA code is in the name (common format: "Airport Name (IATA)")
        name = airport.get("name", "")
        if "(" in name and ")" in name:
            iata = name.split("(")[-1].split(")")[0]
            if len(iata) == 3 and iata.isupper():
                return iata
        
        # Check alternate names for IATA codes
        alternate_names = airport.get("alternateNames", [])
        for alt_name in alternate_names:
            if isinstance(alt_name, dict) and alt_name.get("lang") == "iata":
                return alt_name.get("name")
        
        return None

    def find_airport_code(self, city_name: str) -> Optional[str]:
        """
        Main method: geocode city and find nearest airport with IATA code.
        """
        logger.info(f"Looking up airport for: {city_name}")
        
        # Step 1: Geocode the city
        coords = self.geocode_city(city_name)
        if not coords:
            return None
        
        logger.info(f"Found coordinates for {city_name}: {coords['lat']}, {coords['lon']}")
        
        # Step 2: Find nearby airports
        airports = self.find_nearby_airports(coords['lat'], coords['lon'])
        if not airports:
            return None
        
        # Step 3: Find the first airport with an IATA code
        for airport in airports:
            if airport["iata_code"]:
                logger.info(f"Found airport: {airport['name']} ({airport['iata_code']}) - {airport['distance_km']:.1f}km away")
                return airport["iata_code"]
            # Fallback: try to find IATA code in CSV
            iata_from_csv = self._find_iata_in_csv(airport["name"], city=city_name)
            if iata_from_csv:
                logger.info(f"Found IATA code in CSV for {airport['name']}: {iata_from_csv}")
                return iata_from_csv
        
        logger.warning(f"No airports with IATA codes found near {city_name}")
        return None

    def get_airport_info(self, city_name: str) -> Optional[Dict]:
        """
        Get detailed airport information for a city.
        """
        logger.info(f"Getting airport info for: {city_name}")
        
        # Step 1: Geocode the city
        coords = self.geocode_city(city_name)
        if not coords:
            return None
        
        # Step 2: Find nearby airports
        airports = self.find_nearby_airports(coords['lat'], coords['lon'])
        if not airports:
            return None
        
        # Return the closest airport with IATA code
        for airport in airports:
            if airport["iata_code"]:
                return {
                    "city": city_name,
                    "coordinates": coords,
                    "airport": airport
                }
            iata_from_csv = self._find_iata_in_csv(airport["name"], city=city_name)
            if iata_from_csv:
                airport["iata_code"] = iata_from_csv
                return {
                    "city": city_name,
                    "coordinates": coords,
                    "airport": airport
                }
        
        return None 