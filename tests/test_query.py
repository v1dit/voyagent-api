import sys
from pathlib import Path

# Ensure repository root is on sys.path so `code` package can be imported
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from code.main import app

client = TestClient(app)


def test_query_mock():
    response = client.post("/query", json={"user_query": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "api_response" in data
    # The mock payload places flights under api_response.flights
    assert "flights" in data["api_response"]
