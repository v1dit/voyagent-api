import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load .env variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flight_agent")

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
USE_MOCK = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

class FlightAgent:
    def __init__(self):
        self.api_key = RAPIDAPI_KEY
        # Initialize Groq client if the API key is available. Don't raise on import.
        try:
            if GROQ_API_KEY:
                self.groq = Groq(api_key=GROQ_API_KEY)
            else:
                self.groq = None
                logger.warning("GROQ_API_KEY not set; Groq client disabled")
        except Exception as e:
            self.groq = None
            logger.warning(f"Failed to initialize Groq client: {e}")
        self.sky_id_map = {
            "new york": "NYCA", "dallas": "DFWA", "paris": "PARI",
            "los angeles": "LAXA", "san francisco": "SFOA", "san jose": "SJCA"
        }

    def _get_sky_id(self, city):
        city = city.lower().strip()
        return self.sky_id_map.get(city, city.upper() + "A")

    def extract_with_groq(self, user_query):
        current_year = datetime.now().year

        prompt = f"""
        Today's year is {current_year}.

        Extract structured flight info from the query below.
        Return ONLY valid JSON in this format and nothing else (no markdown or extra explanation):

        {{
          "originCity": "string",
          "destinationCity": "string",
          "departureDate": "YYYY-MM-DD",
          "returnDate": "YYYY-MM-DD",
          "passengers": number
        }}

        Query: {user_query}
        """

        try:
            res = self.groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            content = res.choices[0].message.content.strip()
            print("\n🧪 Raw Groq Output:\n", content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"GROQ parsing error: {e}")
            return {}

    def get_flights(self, origin, destination, departure_date, return_date=None, passengers=1):
        url = "https://flyscraper.p.rapidapi.com/flight/search"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "flyscraper.p.rapidapi.com"
        }

        params = {
            "originSkyId": self._get_sky_id(origin),
            "destinationSkyId": self._get_sky_id(destination),
            "departureDate": departure_date,
            "adults": passengers,
            "cabinClass": "economy",
            "currency": "USD",
            "sort": "best"
        }

        logger.info(f"Querying FlyScraper: {params}")
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"FlyScraper API error: {e}")
            return {"error": str(e)}

    def format_response_with_groq(self, user_query, flight_data):
        prompt = f"""
        You are a helpful travel agent. The user asked:
        "{user_query}"

        Here is the flight data in JSON:
        {json.dumps(flight_data)}

        Summarize the top result conversationally. If flights aren't found or data is incomplete, kindly let the user know.
        """
        try:
            res = self.groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq formatting error: {e}")
            return "Sorry, I couldn't generate a helpful summary."

    def get_flight_recommendations(self, user_query):
        extracted = self.extract_with_groq(user_query)
        logger.info(f"Extracted details: {extracted}")

        required_fields = ["originCity", "destinationCity", "departureDate"]
        if not all(field in extracted and extracted[field] for field in required_fields):
            return {"error": "Missing essential flight details", "details": extracted}

        flights = self.get_flights(
            origin=extracted["originCity"],
            destination=extracted["destinationCity"],
            departure_date=extracted["departureDate"],
            return_date=extracted.get("returnDate"),
            passengers=extracted.get("passengers", 1)
        )

        reply = self.format_response_with_groq(user_query, flights)

        return {
            "extracted_input": extracted,
            "api_response": flights,
            "chatbot_response": reply
        }


# Create a FastAPI app so `uvicorn code.main:app` can import it
app = FastAPI(title="VoyAgent API")

# Simple request model
class QueryRequest(BaseModel):
    user_query: Optional[str] = None


# single agent instance for API use
# Do not create a FlightAgent at import time to avoid side-effects (e.g., missing env vars)
agent = None


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "VoyAgent API running"}


@app.post("/recommendations", tags=["flight"] )
def recommendations(req: QueryRequest):
    if not req.user_query:
        raise HTTPException(status_code=400, detail="`user_query` is required")
    # create agent per-request to avoid import-time side effects; lightweight if Groq not configured
    local_agent = FlightAgent()
    # If mock mode is enabled, return a predictable static response so the app
    # can be demoed without any external API keys.
    if USE_MOCK:
        mock_response = {
            "extracted_input": {
                "originCity": "San Jose",
                "destinationCity": "Dallas",
                "departureDate": "2026-01-15",
                "returnDate": "2026-01-20",
                "passengers": 1
            },
            "api_response": {
                "flights": [
                    {
                        "airline": "DemoAir",
                        "price": "$199",
                        "departure": "2026-01-15T08:00:00",
                        "arrival": "2026-01-15T12:00:00",
                        "duration": "4h"
                    }
                ]
            },
            "chatbot_response": "Top result: DemoAir direct, $199. Departs 08:00, arrives 12:00."
        }
        return mock_response

    return local_agent.get_flight_recommendations(req.user_query)


if __name__ == "__main__":
    agent_cli = FlightAgent()
    query = input("Enter your travel request: ")
    result = agent_cli.get_flight_recommendations(query)

    if "chatbot_response" in result:
        print("\n Chatbot Response:\n" + result["chatbot_response"])
    else:
        print("\n Something went wrong.\nDetails:\n", json.dumps(result, indent=2))
