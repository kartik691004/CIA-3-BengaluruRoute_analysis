from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

client = TestClient(app)

def test_get_graph():
    response = client.get("/graph")
    assert response.status_code == 200
    assert "nodes" in response.json()

def test_compute_route():
    req = {
        "depot": "Majestic",
        "stops": ["Indiranagar", "Koramangala"],
        "algorithm": "two_opt"
    }
    response = client.post("/route", json=req)
    assert response.status_code == 200
    assert "tour" in response.json()

def test_unreachable_node():
    req = {
        "depot": "Majestic",
        "stops": ["Isolated_Test"],
        "algorithm": "nearest_neighbour"
    }
    response = client.post("/route", json=req)
    assert response.status_code == 400
    assert "unreachable" in response.json()["detail"].lower()

def test_compute_route_all():
    req = {
        "depot": "Majestic",
        "stops": ["Indiranagar", "Koramangala", "Whitefield"],
        "algorithm": "all"
    }
    response = client.post("/route", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["compare"] == True
    results = data["results"]
    assert "brute_force" in results
    assert "two_opt" in results
    assert "nearest_neighbour" in results
    
    assert results["brute_force"]["cost"] <= results["two_opt"]["cost"] + 1e-5
    assert results["two_opt"]["cost"] <= results["nearest_neighbour"]["cost"] + 1e-5
    
    assert "distance_km" in results["brute_force"]
    assert "estimated_minutes" in results["brute_force"]
