#!/usr/bin/env python3
"""
Test script for the Intelligent Flight Agent
This agent uses GROQ for query understanding, Aviation Edge for airport codes, and Fly Scraper for flight search.
"""

import sys
import os
sys.path.append('code')

from agents.intelligent_flight_agent import IntelligentFlightAgent

def main():
    # Initialize the intelligent flight agent
    agent = IntelligentFlightAgent()
    
    # Hardcoded query info (bypassing GROQ)
    query_info = {
        'origin_city': 'San Francisco',
        'destination_city': 'Dallas',
        'departure_date': '2025-07-10',
        'return_date': None,
        'passengers': 1,
        'max_price': 500,
        'trip_type': 'one-way'
    }
    print("=== Hardcoded Flight Search Test ===\n")
    print(f"From: {query_info['origin_city']}  To: {query_info['destination_city']}  Date: {query_info['departure_date']}  Max Price: ${query_info['max_price']}")
    print("-" * 50)
    
    # Use the agent's airport lookup
    origin_code = agent.find_airport_code(query_info['origin_city'])
    dest_code = agent.find_airport_code(query_info['destination_city'])
    print(f"Origin IATA: {origin_code}  Destination IATA: {dest_code}")
    
    if not origin_code or not dest_code:
        print("❌ Could not resolve airport codes.")
        return
    
    # Search for flights using Fly Scraper
    flights = agent.search_flights_fly_scraper(
        origin_code, dest_code, query_info['departure_date'],
        query_info['return_date'], query_info['passengers'], query_info['max_price']
    )
    print(f"Found {len(flights)} flights:")
    for i, flight in enumerate(flights[:5], 1):
        price = agent._extract_price(flight)
        print(f"{i}. Price: ${price:.2f}")
        if 'airline' in flight:
            print(f"   Airline: {flight['airline']}")
        if 'flightNumber' in flight:
            print(f"   Flight: {flight['flightNumber']}")
        print()

if __name__ == "__main__":
    main() 