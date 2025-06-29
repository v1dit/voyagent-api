import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime
import logging
from amadeus import Client, ResponseError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('flight_agent')

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

class FlightAgent:
    def __init__(self):
        self.api_key = RAPIDAPI_KEY
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY is not set. API calls will fail.")
        
        # Store SkyID mappings - these would need to be populated with actual values
        # from /get-config endpoint in a production system
        self.sky_id_map = {
            # Major US Cities
            "new york": "NYCA",
            "nyc": "NYCA",
            "manhattan": "NYCA",
            "brooklyn": "NYCA",
            "queens": "NYCA",
            "bronx": "NYCA",
            "staten island": "NYCA",
            
            "los angeles": "LAXA",
            "la": "LAXA",
            "hollywood": "LAXA",
            "beverly hills": "LAXA",
            
            "chicago": "CHIA",
            "houston": "HOUA",
            "dallas": "DFWA",
            "phoenix": "PHXA",
            "san antonio": "SATA",
            "san diego": "SANA",
            "san francisco": "SFOA",
            "sf": "SFOA",
            "san jose": "SJCA",
            "austin": "AUSA",
            "seattle": "SEAA",
            "denver": "DENA",
            "washington": "WASA",
            "dc": "WASA",
            "washington dc": "WASA",
            "boston": "BOSA",
            "miami": "MIAA",
            "atlanta": "ATLA",
            "las vegas": "LASA",
            "vegas": "LASA",
            "philadelphia": "PHLA",
            "detroit": "DETA",
            "portland": "PDXA",
            "orlando": "ORLA",
            "tampa": "TPAA",
            "nashville": "BNAA",
            "new orleans": "MSYA",
            "charlotte": "CLTA",
            "minneapolis": "MSPA",
            "cleveland": "CLEA",
            "pittsburgh": "PITA",
            "cincinnati": "CVGA",
            "kansas city": "MCIA",
            "st louis": "STLA",
            "indianapolis": "INDA",
            "columbus": "CMHA",
            "milwaukee": "MWEA",
            "oklahoma city": "OKCA",
            "memphis": "MEMA",
            "louisville": "SDFA",
            "baltimore": "BWIA",
            "salt lake city": "SLCA",
            "albuquerque": "ABQA",
            "tucson": "TUSA",
            "fresno": "FATA",
            "sacramento": "SMFA",
            "long beach": "LBGA",
            "oakland": "OAKA",
            "bakersfield": "BFLA",
            "anaheim": "SNAA",
            "santa ana": "SNAA",
            "riverside": "ONTAA",
            "stockton": "SCKA",
            "irvine": "SNAA",
            "fremont": "SJCA",
            "san bernardino": "ONTAA",
            "modesto": "MODA",
            "fontana": "ONTAA",
            "oxnard": "OXRA",
            "moreno valley": "ONTAA",
            "glendale": "LAXA",
            "huntington beach": "LBGA",
            "santa clarita": "LAXA",
            "garden grove": "SNAA",
            "oceanside": "SANAA",
            "rancho cucamonga": "ONTAA",
            "santa rosa": "STSA",
            "ontario": "ONTAA",
            "elk grove": "SMFA",
            "corona": "ONTAA",
            "lancaster": "LAXA",
            "palmdale": "LAXA",
            "salinas": "SJCA",
            "hayward": "OAKA",
            "pomona": "ONTAA",
            "escondido": "SANAA",
            "sunnyvale": "SJCA",
            "torrance": "LAXA",
            "pasadena": "LAXA",
            "orange": "SNAA",
            "fullerton": "SNAA",
            "thousand oaks": "LAXA",
            "visalia": "FATA",
            "simi valley": "LAXA",
            "concord": "OAKA",
            "roseville": "SMFA",
            "santa clara": "SJCA",
            "vallejo": "OAKA",
            "victorville": "ONTAA",
            "elgin": "CHIA",
            "springfield": "CHIA",
            "peoria": "CHIA",
            "rockford": "CHIA",
            "joliet": "CHIA",
            "naperville": "CHIA",
            "springfield": "CHIA",
            "peoria": "CHIA",
            "rockford": "CHIA",
            "joliet": "CHIA",
            "naperville": "CHIA",
            "champaign": "CHIA",
            "bloomington": "CHIA",
            "decatur": "CHIA",
            "arlington heights": "CHIA",
            "evanston": "CHIA",
            "schaumburg": "CHIA",
            "bolingbrook": "CHIA",
            "palatine": "CHIA",
            "skokie": "CHIA",
            "des plaines": "CHIA",
            "orland park": "CHIA",
            "tinley park": "CHIA",
            "oak lawn": "CHIA",
            "berwyn": "CHIA",
            "mount prospect": "CHIA",
            "normal": "CHIA",
            "wheaton": "CHIA",
            "hoffman estates": "CHIA",
            "oak park": "CHIA",
            "downers grove": "CHIA",
            "elmhurst": "CHIA",
            "dekalb": "CHIA",
            "glenview": "CHIA",
            "lombard": "CHIA",
            "belleville": "CHIA",
            "moline": "CHIA",
            "east st louis": "STLA",
            "rock island": "CHIA",
            "galesburg": "CHIA",
            "quincy": "CHIA",
            "danville": "CHIA",
            "charleston": "CHIA",
            "mattoon": "CHIA",
            "effingham": "CHIA",
            "carbondale": "CHIA",
            "marion": "CHIA",
            "belleville": "CHIA",
            "moline": "CHIA",
            "east st louis": "STLA",
            "rock island": "CHIA",
            "galesburg": "CHIA",
            "quincy": "CHIA",
            "danville": "CHIA",
            "charleston": "CHIA",
            "mattoon": "CHIA",
            "effingham": "CHIA",
            "carbondale": "CHIA",
            "marion": "CHIA",
            
            # International Cities
            "paris": "PARI",
            "london": "LONA",
            "tokyo": "TYOA",
            "beijing": "PEKA",
            "shanghai": "SHAA",
            "mumbai": "BOMA",
            "delhi": "DELA",
            "sydney": "SYDA",
            "melbourne": "MELA",
            "toronto": "YTOA",
            "vancouver": "YVRA",
            "montreal": "YMQA",
            "mexico city": "MEXA",
            "sao paulo": "GRUA",
            "rio de janeiro": "RIOA",
            "buenos aires": "BUEA",
            "madrid": "MADA",
            "barcelona": "BCNA",
            "rome": "ROMA",
            "milan": "MILA",
            "berlin": "BERA",
            "munich": "MUNCH",
            "frankfurt": "FRAA",
            "amsterdam": "AMSA",
            "brussels": "BRUA",
            "zurich": "ZRHA",
            "vienna": "VIEA",
            "prague": "PRGA",
            "budapest": "BUDA",
            "warsaw": "WARA",
            "moscow": "MOWA",
            "st petersburg": "LEDA",
            "istanbul": "ISTA",
            "dubai": "DXBA",
            "abu dhabi": "AUHA",
            "doha": "DOHA",
            "riyadh": "RUHA",
            "jeddah": "JEDA",
            "cairo": "CAA",
            "nairobi": "NBRA",
            "lagos": "LOSA",
            "johannesburg": "JNBSA",
            "cape town": "CPTA",
            "seoul": "SELA",
            "osaka": "OSAA",
            "kyoto": "OSAA",
            "hong kong": "HKGA",
            "singapore": "SINA",
            "bangkok": "BKKA",
            "manila": "MNLA",
            "jakarta": "CGKA",
            "kuala lumpur": "KULA",
            "ho chi minh city": "SGN",
            "hanoi": "HANA",
            "phnom penh": "PNHA",
            "vientiane": "VTE",
            "yangon": "RGN",
            "dhaka": "DACA",
            "kolkata": "CCUA",
            "chennai": "MAAA",
            "bangalore": "BLRA",
            "hyderabad": "HYDA",
            "pune": "PNQA",
            "ahmedabad": "AMDA",
            "surat": "STVA",
            "jaipur": "JAI",
            "lucknow": "LKO",
            "kanpur": "KNU",
            "nagpur": "NAG",
            "indore": "IDR",
            "thane": "BOMA",
            "bhopal": "BHO",
            "visakhapatnam": "VTZ",
            "patna": "PAT",
            "vadodara": "BDQ",
            "ghaziabad": "DELA",
            "ludhiana": "LUH",
            "agra": "AGR",
            "nashik": "ISK",
            "faridabad": "DELA",
            "meerut": "DELA",
            "rajkot": "RAJ",
            "kalyan": "BOMA",
            "vasai": "BOMA",
            "vashi": "BOMA",
            "aurangabad": "IXU",
            "dombivli": "BOMA",
            "ahmednagar": "BOMA",
            "solapur": "SSE",
            "bhiwandi": "BOMA",
            "srinagar": "SXR",
            "guwahati": "GAU",
            "chandigarh": "IXC",
            "amritsar": "ATQ",
            "varanasi": "VNS",
            "allahabad": "IXD",
            "ranchi": "IXR",
            "howrah": "CCUA",
            "coimbatore": "CJB",
            "jabalpur": "JLR",
            "gwalior": "GWL",
            "vijayawada": "VGA",
            "jodhpur": "JDH",
            "madurai": "IXM",
            "raipur": "RPR",
            "kota": "KTU",
            "guwahati": "GAU",
            "chandigarh": "IXC",
            "amritsar": "ATQ",
            "varanasi": "VNS",
            "allahabad": "IXD",
            "ranchi": "IXR",
            "howrah": "CCUA",
            "coimbatore": "CJB",
            "jabalpur": "JLR",
            "gwalior": "GWL",
            "vijayawada": "VGA",
            "jodhpur": "JDH",
            "madurai": "IXM",
            "raipur": "RPR",
            "kota": "KTU"
        }
        
        self.amadeus = Client(
            client_id=AMADEUS_API_KEY,
            client_secret=AMADEUS_API_SECRET
        )
        
    def _get_sky_id(self, city):
        """
        Convert city name to SkyScanner skyId format
        """
        city = city.lower()
        return self.sky_id_map.get(city, city.upper() + "A")  # Fallback format

    def search_airport_code(self, city_name):
        """
        Search for airport code using the Fly Scraper API
        """
        if not self.api_key:
            logger.error("No API key available for airport search")
            return None
            
        url = "https://flyscraper.p.rapidapi.com/airport/search"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "flyscraper.p.rapidapi.com"
        }
        
        params = {
            "query": city_name,
            "limit": 5  # Get top 5 matches
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            airports = data.get("data", [])
            if airports:
                # Return the first (most relevant) airport's skyId
                return airports[0].get("skyId")
            else:
                logger.warning(f"No airports found for: {city_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for airport code for {city_name}: {str(e)}")
            return None

    def get_sky_id_dynamic(self, city):
        """
        Get SkyID dynamically from API or fall back to cached mapping
        """
        # First try the cached mapping
        city_lower = city.lower()
        if city_lower in self.sky_id_map:
            logger.info(f"Found {city} in hard-coded mapping: {self.sky_id_map[city_lower]}")
            return self.sky_id_map[city_lower]
        
        # If not in cache, try API search (but be careful with rate limits)
        logger.info(f"City {city} not in hard-coded mapping, trying API search...")
        sky_id = self.search_airport_code(city)
        if sky_id:
            # Cache the result for future use
            self.sky_id_map[city_lower] = sky_id
            logger.info(f"Found {city} via API: {sky_id}")
            return sky_id
        
        # If API search fails, try some common variations
        variations = [
            city,
            city.replace(" ", ""),
            city.split()[0] if " " in city else city,  # First word
            city.replace("new york", "nyc").replace("los angeles", "la")
        ]
        
        for variation in variations:
            if variation != city:  # Skip if we already tried this
                logger.info(f"Trying variation: {variation}")
                sky_id = self.search_airport_code(variation)
                if sky_id:
                    self.sky_id_map[city_lower] = sky_id
                    logger.info(f"Found {city} via variation {variation}: {sky_id}")
                    return sky_id
        
        logger.error(f"Could not find SkyID for city: {city}")
        return None

    def extract_flight_details(self, query):
        """
        Extract flight details from natural language query
        """
        origin_match = re.search(r'from\s+([A-Za-z\s]+?)\s+to', query)
        dest_match = re.search(r'to\s+([A-Za-z\s]+?)(?:\s|\.|$)', query)
        
        # More complex date patterns
        date_match = re.search(r'from\s+(\w+)\s+(\d+)(?:st|nd|rd|th)?\s+to\s+(\w+)\s+(\d+)(?:st|nd|rd|th)?', query, re.IGNORECASE)
        if not date_match:
            date_match = re.search(r'(\w+)\s+(\d+)(?:st|nd|rd|th)?\s+to\s+(\w+)\s+(\d+)(?:st|nd|rd|th)?', query, re.IGNORECASE)
        
        budget_match = re.search(r'budget\s+(?:is\s+|of\s+)?[$]?(\d+)', query)
        people_match = re.search(r'(\d+)\s+(?:people|persons|passengers)', query)

        origin = origin_match.group(1).strip() if origin_match else ""
        destination = dest_match.group(1).strip() if dest_match else ""

        current_year = datetime.now().year
        depart = return_ = None
        if date_match:
            try:
                depart_month = datetime.strptime(date_match.group(1), '%B').month
            except ValueError:
                # Try abbreviated month name
                try:
                    depart_month = datetime.strptime(date_match.group(1), '%b').month
                except ValueError:
                    depart_month = None
                    
            try:
                return_month = datetime.strptime(date_match.group(3), '%B').month
            except ValueError:
                # Try abbreviated month name
                try:
                    return_month = datetime.strptime(date_match.group(3), '%b').month
                except ValueError:
                    return_month = None
                
            if depart_month and return_month:
                depart = f"{current_year}-{depart_month:02d}-{int(date_match.group(2)):02d}"
                return_ = f"{current_year}-{return_month:02d}-{int(date_match.group(4)):02d}"

        budget = float(budget_match.group(1)) if budget_match else None
        passengers = int(people_match.group(1)) if people_match else 1

        return {
            "origin": origin,
            "destination": destination,
            "departure_date": depart,
            "return_date": return_,
            "budget": budget,
            "passengers": passengers,
            "flight_budget": 0.4 * budget if budget else None
        }

    def get_flights(self, origin, destination, departure_date, return_date=None, passengers=1):
        """
        Search for flights using the Fly Scraper API with proper parameters
        """
        origin_sky_id = self.get_sky_id_dynamic(origin)
        dest_sky_id = self.get_sky_id_dynamic(destination)
        
        # Check if we successfully got airport codes
        if not origin_sky_id:
            return {"error": f"Could not find airport code for origin: {origin}"}
        if not dest_sky_id:
            return {"error": f"Could not find airport code for destination: {destination}"}

        url = "https://flyscraper.p.rapidapi.com/flight/search"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "flyscraper.p.rapidapi.com"
        }
        
        # Format date as required by API (YYYY-MM-DD)
        departure_formatted = departure_date
        
        # Set up query parameters according to API documentation
        params = {
            "originSkyId": origin_sky_id,
            "destinationSkyId": dest_sky_id,
            "departureDate": departure_formatted,
            "adults": passengers,
            "cabinClass": "economy",
            "currency": "USD",
            "sort": "price"  # Sort by price to find cheapest flights
        }
        
        # Add return date if provided for roundtrip flights
        if return_date:
            params["returnDate"] = return_date

        logger.info(f"Searching flights: {origin_sky_id} -> {dest_sky_id} on {departure_formatted}")
        if return_date:
            logger.info(f"Return flight on: {return_date}")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            logger.info(f"API request URL: {response.url}")
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we need to handle incomplete results
            if data.get("data", {}).get("context", {}).get("status") == "incomplete":
                # In a real implementation, you'd call the /flight/search-incomplete endpoint
                # until the status is 'complete', but for simplicity we'll just return what we have
                logger.warning("Received incomplete results. In production, should poll until complete.")
            
            # Process the flight results to extract useful information
            return self._process_flight_results(data, return_date)
        except Exception as e:
            logger.error(f"Error getting flights: {str(e)}")
            return {"error": str(e)}

    def _process_flight_results(self, api_response, return_date=None):
        """
        Process and simplify the flight API response
        """
        try:
            # Check if we have itineraries
            itineraries = api_response.get("data", {}).get("itineraries", [])
            
            if not itineraries:
                return {"data": [], "count": 0, "message": "No flights found"}
            
            processed_flights = []
            
            # Extract relevant flight information
            for itinerary in itineraries[:10]:  # Limit to top 10 flights
                legs = itinerary.get("legs", [])
                if not legs:
                    continue
                
                # Extract price
                price_info = itinerary.get("pricing", {}).get("pricingOptions", [{}])[0]
                price = price_info.get("price", {}).get("amount", "N/A")
                
                # Handle roundtrip flights (2 legs) or one-way flights (1 leg)
                if len(legs) == 2 and return_date:
                    # Roundtrip flight
                    outbound_leg = legs[0]
                    return_leg = legs[1]
                    
                    # Extract outbound flight details
                    outbound_carriers = outbound_leg.get("carriers", {})
                    outbound_marketing = outbound_carriers.get("marketing", [{}])[0]
                    outbound_airline = outbound_marketing.get("name", "Unknown Airline")
                    outbound_flight = outbound_marketing.get("flightNumber", "")
                    
                    # Extract return flight details
                    return_carriers = return_leg.get("carriers", {})
                    return_marketing = return_carriers.get("marketing", [{}])[0]
                    return_airline = return_marketing.get("name", "Unknown Airline")
                    return_flight = return_marketing.get("flightNumber", "")
                    
                    processed_flight = {
                        "type": "roundtrip",
                        "price": price,
                        "outbound": {
                            "airline": outbound_airline,
                            "flightNumber": outbound_flight,
                            "departureTime": outbound_leg.get("departure", {}).get("time", ""),
                            "arrivalTime": outbound_leg.get("arrival", {}).get("time", ""),
                            "stops": outbound_leg.get("stopCount", 0),
                            "duration": outbound_leg.get("durationInMinutes", 0)
                        },
                        "return": {
                            "airline": return_airline,
                            "flightNumber": return_flight,
                            "departureTime": return_leg.get("departure", {}).get("time", ""),
                            "arrivalTime": return_leg.get("arrival", {}).get("time", ""),
                            "stops": return_leg.get("stopCount", 0),
                            "duration": return_leg.get("durationInMinutes", 0)
                        },
                        "itineraryId": itinerary.get("id", "")
                    }
                else:
                    # One-way flight
                    leg = legs[0]
                carriers = leg.get("carriers", {})
                marketing = carriers.get("marketing", [{}])[0]
                airline_name = marketing.get("name", "Unknown Airline")
                flight_number = marketing.get("flightNumber", "")
                
                processed_flight = {
                        "type": "one-way",
                    "airline": airline_name,
                    "flightNumber": flight_number,
                    "price": price,
                        "departureTime": leg.get("departure", {}).get("time", ""),
                        "arrivalTime": leg.get("arrival", {}).get("time", ""),
                        "stops": leg.get("stopCount", 0),
                        "duration": leg.get("durationInMinutes", 0),
                    "itineraryId": itinerary.get("id", "")
                }
                
                processed_flights.append(processed_flight)
            
            # Sort by price (cheapest first) - convert price to float for sorting
            def get_price_for_sorting(flight):
                try:
                    return float(flight.get("price", 0))
                except (ValueError, TypeError):
                    return float('inf')  # Put flights with invalid prices at the end
            
            processed_flights.sort(key=get_price_for_sorting)
            
            return {
                "data": processed_flights,
                "count": len(processed_flights)
            }
            
        except Exception as e:
            logger.error(f"Error processing flight results: {str(e)}")
            return {"data": [], "count": 0, "error": str(e)}

    def get_flight_recommendations(self, user_query):
        """
        Main function to extract details from query and get flight recommendations
        """
        details = self.extract_flight_details(user_query)
        logger.info(f"Extracted details: {details}")

        if not all([details['origin'], details['destination'], details['departure_date']]):
            return {"error": "Missing critical info (origin, destination, or date) in query.", "details": details}

        # Get airport codes and log them for debugging
        origin_sky_id = self.get_sky_id_dynamic(details["origin"])
        dest_sky_id = self.get_sky_id_dynamic(details["destination"])
        
        logger.info(f"Found airport codes - Origin: {details['origin']} -> {origin_sky_id}")
        logger.info(f"Found airport codes - Destination: {details['destination']} -> {dest_sky_id}")

        result = self.get_flights(
            details["origin"],
            details["destination"],
            details["departure_date"],
            details["return_date"],
            details["passengers"]
        )

        # Add airport code information to the response for debugging
        response = {**result, "extracted": details}
        if "error" not in result:
            response["airport_codes"] = {
                "origin": {"city": details["origin"], "skyId": origin_sky_id},
                "destination": {"city": details["destination"], "skyId": dest_sky_id}
            }

        return response

    def city_to_airport(self, city_name):
        try:
            response = self.amadeus.reference_data.locations.get(
                keyword=city_name,
                subType='AIRPORT,CITY'
            )
            return response.data[0]['iataCode']
        except Exception as e:
            print(f"[Airport Lookup Error] {e}")
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


# Example usage
if __name__ == "__main__":
    agent = FlightAgent()
    
    # Test with a roundtrip query
    test_query = "plan me a 3 day trip to Dallas, Texas from New York from July 10th to July 13th, 2025. Budget is 500 for 2 people"
    print(f"Testing query: {test_query}")
    print("=" * 60)
    
    result = agent.get_flight_recommendations(test_query)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Success! Found {result.get('count', 0)} flights")
        
        # Show airport codes found
        if "airport_codes" in result:
            codes = result["airport_codes"]
            print(f"Airport codes:")
            print(f"  Origin: {codes['origin']['city']} -> {codes['origin']['skyId']}")
            print(f"  Destination: {codes['destination']['city']} -> {codes['destination']['skyId']}")
        
        # Show extracted details
        if "extracted" in result:
            details = result["extracted"]
            print(f"Extracted details:")
            print(f"  Route: {details['origin']} to {details['destination']}")
            print(f"  Dates: {details['departure_date']} to {details['return_date']}")
            print(f"  Passengers: {details['passengers']}")
            print(f"  Budget: ${details['budget']}")
        
        # Show top 3 cheapest flights
        if result.get("data"):
            print(f"\nTop 3 cheapest flights:")
            for i, flight in enumerate(result["data"][:3], 1):
                if flight.get("type") == "roundtrip":
                    print(f"  {i}. ${flight.get('price', 'N/A')} - {flight['outbound']['airline']} (Roundtrip)")
                else:
                    print(f"  {i}. ${flight.get('price', 'N/A')} - {flight.get('airline', 'Unknown')} (One-way)")
    
    print("\n" + "=" * 60)