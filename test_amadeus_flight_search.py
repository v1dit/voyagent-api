import os
from amadeus import Client, ResponseError
from dotenv import load_dotenv
import requests

load_dotenv()
print("CLIENT_ID:", os.getenv("AMADEUS_CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("AMADEUS_CLIENT_SECRET"))

# Check Amadeus API connectivity
try:
    resp = requests.get("https://test.api.amadeus.com/v1/reference-data/locations?keyword=SFO&subType=AIRPORT")
    print(f"Amadeus API connectivity status: {resp.status_code}")
except Exception as e:
    print(f"Amadeus API connectivity error: {e}")

class FlightAgent:
    def __init__(self):
        self.amadeus = Client(
            client_id=os.getenv("AMADEUS_CLIENT_ID"),
            client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
        )

    def city_to_airport(self, city_name):
        try:
            response = self.amadeus.reference_data.locations.get(
                keyword=city_name,
                subType='AIRPORT,CITY'
            )
            print(f"API Response for {city_name}: {response.data}")
            return response.data[0]['iataCode']
        except Exception as e:
            print(f"[Airport Lookup Error for {city_name}] Type: {type(e).__name__}, Message: {str(e)}")
            return None

    def search_flights(self, origin_city, dest_city, depart_date, return_date, max_price=None, adults=1):
        origin_code = self.city_to_airport(origin_city)
        dest_code = self.city_to_airport(dest_city)

        if not origin_code or not dest_code:
            print("Could not resolve city to airport.")
            return []

        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=dest_code,
                departureDate=depart_date,
                returnDate=return_date,
                adults=adults,
                maxPrice=max_price,
                currencyCode="USD"
            )
            return response.data
        except Exception as e:
            print(f"[Flight Search Error] {e}")
            return []

if __name__ == "__main__":
    agent = FlightAgent()
    
    # Test with hardcoded airport codes to bypass the failing airport lookup
    try:
        response = agent.amadeus.shopping.flight_offers_search.get(
            originLocationCode="SFO",
            destinationLocationCode="DFW", 
            departureDate="2025-07-10",
            returnDate="2025-07-13",
            adults=1,
            maxPrice=500,
            currencyCode="USD"
        )
        print(f"Direct flight search response: {len(response.data)} flights found")
        for i, flight in enumerate(response.data[:3], 1):
            price = flight['price']['total'] if 'price' in flight else 'N/A'
            print(f"{i}. Price: ${price}")
            print(f"   Itinerary: {flight.get('itineraries', [{}])[0]}")
            print()
    except Exception as e:
        print(f"Direct flight search error: {type(e).__name__}, Message: {str(e)}")
    
    # Original test (will fail at airport lookup)
    print("\n--- Original test with city names ---")
    flights = agent.search_flights("San Francisco", "Dallas", "2025-07-10", "2025-07-13", max_price=500, adults=1)
    print(f"Found {len(flights)} flights:")
    for i, flight in enumerate(flights[:3], 1):
        price = flight['price']['total'] if 'price' in flight else 'N/A'
        print(f"{i}. Price: ${price}")
        print(f"   Itinerary: {flight.get('itineraries', [{}])[0]}")
        print() 