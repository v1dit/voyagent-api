#!/usr/bin/env python3
"""
Test script for the improved FlightAgent with dynamic airport code lookup
"""

import os
from code.agents.flight_agent import FlightAgent

def test_flight_agent():
    """Test the FlightAgent with various queries"""
    
    # Initialize the agent
    agent = FlightAgent()
    
    # Test queries
    test_queries = [
        "Find flights from New York to Los Angeles on July 15th 2025 for 2 people",
        "I need a roundtrip from Chicago to Miami from August 10th to August 15th 2025",
        "Search for flights from Seattle to Denver on September 5th 2025",
        "Book a flight from Boston to Atlanta on October 20th 2025 for 1 person"
    ]
    
    print("Testing FlightAgent with dynamic airport code lookup...")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            result = agent.get_flight_recommendations(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success! Found {result.get('count', 0)} flights")
                
                # Show airport codes found
                if "airport_codes" in result:
                    codes = result["airport_codes"]
                    print(f"   Origin: {codes['origin']['city']} -> {codes['origin']['skyId']}")
                    print(f"   Destination: {codes['destination']['city']} -> {codes['destination']['skyId']}")
                
                # Show extracted details
                if "extracted" in result:
                    details = result["extracted"]
                    print(f"   Extracted: {details['origin']} to {details['destination']}")
                    print(f"   Dates: {details['departure_date']} to {details['return_date']}")
                    print(f"   Passengers: {details['passengers']}")
                
                # Show cheapest flight if available
                if result.get("data"):
                    cheapest = result["data"][0]
                    print(f"   Cheapest: ${cheapest.get('price', 'N/A')} - {cheapest.get('airline', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print()

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("RAPIDAPI_KEY"):
        print("⚠️  Warning: RAPIDAPI_KEY environment variable not set!")
        print("   Set it with: export RAPIDAPI_KEY='your_api_key_here'")
        print("   The agent will still work for testing airport code lookup.")
    
    test_flight_agent() 