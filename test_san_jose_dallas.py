#!/usr/bin/env python3
"""
Test script for San Jose to Dallas flight query
"""

from code.agents.flight_agent import FlightAgent

def test_san_jose_dallas():
    """Test the FlightAgent with San Jose to Dallas query"""
    
    # Initialize the agent
    agent = FlightAgent()
    
    # Test query
    query = "Find flights from San Jose to Dallas Texas for a trip that leaves on July 10 to July 13"
    print(f"Testing query: {query}")
    print("=" * 60)
    
    try:
        result = agent.get_flight_recommendations(query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success! Found {result.get('count', 0)} flights")
            
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
            
            # Show top 3 cheapest flights
            if result.get("data"):
                print(f"\nTop 3 cheapest flights:")
                for i, flight in enumerate(result["data"][:3], 1):
                    if flight.get("type") == "roundtrip":
                        print(f"  {i}. ${flight.get('price', 'N/A')} - {flight['outbound']['airline']} (Roundtrip)")
                    else:
                        print(f"  {i}. ${flight.get('price', 'N/A')} - {flight.get('airline', 'Unknown')} (One-way)")
            else:
                print("No flight data found")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_san_jose_dallas() 