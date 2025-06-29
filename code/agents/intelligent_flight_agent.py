import requests
import os
import re
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from .free_airport_lookup import FreeAirportLookup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('intelligent_flight_agent')

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

class IntelligentFlightAgent:
    def __init__(self):
        self.groq_api_key = GROQ_API_KEY
        self.rapidapi_key = RAPIDAPI_KEY
        self.airport_lookup = FreeAirportLookup()
        
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY is not set. Query understanding will fail.")
        if not self.rapidapi_key:
            logger.warning("RAPIDAPI_KEY is not set. Fly Scraper API calls will fail.")

    def understand_query(self, user_query: str) -> Dict:
        """
        Use GROQ to understand the user's flight search query and extract structured information.
        """
        if not self.groq_api_key:
            logger.error("GROQ API key not available")
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
                "Authorization": f"Bearer {self.groq_api_key}",
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
                
                # Try to parse the JSON response
                try:
                    parsed = json.loads(content)
                    logger.info(f"Query understood: {parsed}")
                    return parsed
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse GROQ response as JSON: {content}")
                    return {}
            else:
                logger.error(f"GROQ API error: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error calling GROQ API: {e}")
            return {}

    def find_airport_code(self, city_name: str) -> Optional[str]:
        """
        Use robust airport lookup (GeoNames + airports.csv fallback) to find the IATA code for a given city.
        """
        return self.airport_lookup.find_airport_code(city_name)

    def search_flights_fly_scraper(self, origin_code: str, dest_code: str, 
                                 departure_date: str, return_date: Optional[str] = None,
                                 passengers: int = 1, max_price: Optional[int] = None) -> List[Dict]:
        """
        Use Fly Scraper API to search for flights between airports.
        """
        if not self.rapidapi_key:
            logger.error("RapidAPI key not available")
            return []
        
        try:
            url = "https://fly-scraper.p.rapidapi.com/search"
            
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "fly-scraper.p.rapidapi.com"
            }
            
            payload = {
                "from": origin_code,
                "to": dest_code,
                "date": departure_date,
                "adults": passengers,
                "type": "roundtrip" if return_date else "oneway"
            }
            
            if return_date:
                payload["returnDate"] = return_date
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data']:
                    flights = data['data']
                    
                    # Filter by max price if specified
                    if max_price:
                        flights = [f for f in flights if self._extract_price(f) <= max_price]
                    
                    # Sort by price
                    flights.sort(key=self._extract_price)
                    
                    logger.info(f"Found {len(flights)} flights")
                    return flights
                else:
                    logger.warning("No flights found in response")
                    return []
            else:
                logger.error(f"Fly Scraper API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error calling Fly Scraper API: {e}")
            return []

    def _extract_price(self, flight: Dict) -> float:
        """Extract price from flight data for sorting."""
        try:
            # Try different possible price fields
            if 'price' in flight:
                if isinstance(flight['price'], dict):
                    return float(flight['price'].get('total', 0))
                else:
                    return float(flight['price'])
            elif 'totalPrice' in flight:
                return float(flight['totalPrice'])
            else:
                return float('inf')  # Put flights without price at the end
        except (ValueError, TypeError):
            return float('inf')

    def search_flights(self, user_query: str) -> Dict:
        """
        Main method to search flights using natural language query.
        """
        logger.info(f"Processing query: {user_query}")
        
        # Step 1: Understand the query using GROQ
        query_info = self.understand_query(user_query)
        if not query_info:
            return {"error": "Failed to understand query", "flights": []}
        
        # Step 2: Find airport codes using Aviation Edge
        origin_city = query_info.get('origin_city')
        destination_city = query_info.get('destination_city')
        
        if not origin_city or not destination_city:
            return {"error": "Could not identify origin or destination", "flights": []}
        
        origin_code = self.find_airport_code(origin_city)
        dest_code = self.find_airport_code(destination_city)
        
        if not origin_code or not dest_code:
            return {"error": f"Could not find airport codes for {origin_city} or {destination_city}", "flights": []}
        
        # Step 3: Search for flights using Fly Scraper
        departure_date = query_info.get('departure_date')
        return_date = query_info.get('return_date')
        passengers = query_info.get('passengers', 1)
        max_price = query_info.get('max_price')
        
        if not departure_date:
            return {"error": "No departure date specified", "flights": []}
        
        flights = self.search_flights_fly_scraper(
            origin_code, dest_code, departure_date, return_date, 
            passengers, max_price
        )
        
        return {
            "query_info": query_info,
            "airports": {
                "origin": {"city": origin_city, "code": origin_code},
                "destination": {"city": destination_city, "code": dest_code}
            },
            "flights": flights,
            "total_flights": len(flights)
        }

    def format_flight_results(self, results: Dict) -> str:
        """
        Format flight results into a readable string.
        """
        if "error" in results:
            return f"Error: {results['error']}"
        
        output = []
        query_info = results.get('query_info', {})
        airports = results.get('airports', {})
        flights = results.get('flights', [])
        
        output.append(f"Flight Search Results:")
        output.append(f"From: {airports.get('origin', {}).get('city')} ({airports.get('origin', {}).get('code')})")
        output.append(f"To: {airports.get('destination', {}).get('city')} ({airports.get('destination', {}).get('code')})")
        output.append(f"Date: {query_info.get('departure_date')}")
        if query_info.get('return_date'):
            output.append(f"Return: {query_info.get('return_date')}")
        output.append(f"Passengers: {query_info.get('passengers', 1)}")
        if query_info.get('max_price'):
            output.append(f"Max Price: ${query_info.get('max_price')}")
        output.append(f"Found {len(flights)} flights\n")
        
        for i, flight in enumerate(flights[:5], 1):  # Show top 5 flights
            price = self._extract_price(flight)
            output.append(f"{i}. Price: ${price:.2f}")
            
            # Try to extract airline and flight info
            if 'airline' in flight:
                output.append(f"   Airline: {flight['airline']}")
            if 'flightNumber' in flight:
                output.append(f"   Flight: {flight['flightNumber']}")
            
            output.append("")
        
        return "\n".join(output) 