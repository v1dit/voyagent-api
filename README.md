# VoyAgent API - Intelligent Flight Search Agent

An intelligent Python-based flight search system that understands natural language queries and finds the cheapest flights using multiple APIs and data sources.

## Features

- **Natural Language Processing**: Uses GROQ LLM to understand flight queries like "I want to fly from San Francisco to Dallas on July 10th for under $500"
- **Robust Airport Lookup**: Combines OpenStreetMap (Nominatim), GeoNames, and local airports.csv for reliable city-to-airport code mapping
- **Real Flight Data**: Integrates with Fly Scraper API for actual flight search results
- **Fallback Systems**: Multiple data sources ensure high reliability even when some APIs are unavailable
- **Price Filtering**: Automatically filters results by price constraints
- **Flexible Query Support**: Handles one-way, roundtrip, and multi-city flights

## Architecture

```
User Query → GROQ (Query Understanding) → Nominatim (Geocoding) → 
GeoNames + airports.csv (IATA Code) → Fly Scraper (Real Flights)
```

## Prerequisites

- Python 3.8+
- API keys for:
  - GROQ (for natural language processing)
  - GeoNames (for airport lookup)
  - Fly Scraper (for flight search)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd voyagent-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Download airports data:
```bash
# The airports.csv file should be included in the repository
# If not, download from: https://ourairports.com/data/airports.csv
```

## Configuration

Create a `.env` file with your API credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
GEONAMES_USERNAME=your_geonames_username_here
FLY_SCRAPER_API_KEY=your_fly_scraper_api_key_here
```

## Usage

### Basic Usage

```python
from code.agents.intelligent_flight_agent import IntelligentFlightAgent

# Initialize the agent
agent = IntelligentFlightAgent()

# Search for flights using natural language
query = "I want to fly from San Francisco to Dallas on July 10th for under $500"
results = agent.search_flights(query)

# Format and display results
formatted_results = agent.format_flight_results(results)
print(formatted_results)
```

### Direct Airport Lookup

```python
from code.agents.free_airport_lookup import FreeAirportLookup

lookup = FreeAirportLookup()
airport_code = lookup.find_airport_code("San Francisco")
print(f"Airport code: {airport_code}")  # Output: SFO
```

### Testing

Run the test suite:

```bash
# Test the intelligent flight agent
python test_intelligent_flight_agent.py

# Test airport lookup
python test_free_airport_lookup.py

# Test individual components
python test_amadeus_flight_search.py
python test_geocoding.py
```

## Project Structure

```
voyagent-api/
├── code/
│   ├── agents/
│   │   ├── intelligent_flight_agent.py    # Main flight search agent
│   │   ├── free_airport_lookup.py         # Airport code resolution
│   │   ├── flight_agent.py                # Basic flight agent
│   │   └── __init__.py
│   ├── main.py                            # Main application entry point
│   └── __init__.py
├── airports.csv                           # Global airport database
├── requirements.txt                       # Python dependencies
├── README.md                             # This file
├── .env.example                          # Environment variables template
├── .gitignore                            # Git ignore rules
└── test_*.py                             # Test files
```

## API Dependencies

### GROQ
- **Purpose**: Natural language query understanding
- **Cost**: Pay-per-use
- **Setup**: Sign up at https://console.groq.com/

### GeoNames
- **Purpose**: Geographic data and airport information
- **Cost**: Free (with registration)
- **Setup**: Register at http://www.geonames.org/login

### Fly Scraper
- **Purpose**: Real flight search data
- **Cost**: Varies by plan
- **Setup**: Sign up at their website

### OpenStreetMap (Nominatim)
- **Purpose**: Geocoding cities to coordinates
- **Cost**: Free
- **Setup**: No registration required

## Development

### Adding New Features

1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes
3. Add tests
4. Submit pull request

### Testing

The project includes comprehensive tests for each component:

- `test_intelligent_flight_agent.py`: End-to-end testing
- `test_free_airport_lookup.py`: Airport lookup testing
- `test_amadeus_flight_search.py`: Flight search testing
- `test_geocoding.py`: Geocoding functionality testing

## Troubleshooting

### Common Issues

1. **GROQ API 503 Error**: Service temporarily unavailable, retry later
2. **GeoNames 401 Error**: Check username and account activation
3. **Fly Scraper 404 Error**: Verify API endpoint and credentials
4. **Missing airports.csv**: Download from OurAirports website

### Debug Mode

Enable debug logging by setting the log level in your code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OurAirports](https://ourairports.com/) for the comprehensive airport database
- [GeoNames](http://www.geonames.org/) for geographic data
- [OpenStreetMap](https://www.openstreetmap.org/) for geocoding services
- [GROQ](https://console.groq.com/) for natural language processing 