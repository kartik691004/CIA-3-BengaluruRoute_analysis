import os
import sys
import pytest
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.graph import generate_graph
from algorithms.tsp import nearest_neighbour, two_opt, brute_force

@pytest.fixture(scope="module")
def graph():
    return generate_graph(filepath=None)

def test_single_stop(graph):
    tour, cost, _, _ = nearest_neighbour(graph, "Majestic", ["Indiranagar"])
    assert tour == ["Majestic", "Indiranagar"]

def test_duplicate_stops(graph):
    tour, cost, _, _ = nearest_neighbour(graph, "Majestic", ["Indiranagar", "Indiranagar"])
    assert len(tour) == 2
    assert tour == ["Majestic", "Indiranagar"]

def test_unreachable(graph):
    tour, cost, _, error = nearest_neighbour(graph, "Majestic", ["Isolated_Test"])
    assert tour is None
    assert error is not None

def test_two_opt_improves_or_equals(graph):
    nodes = list(graph["nodes"].keys())
    nodes.remove("Isolated_Test")
    
    for _ in range(50):
        stops = random.sample(nodes, 6)
        depot = stops[0]
        others = stops[1:]
        
        _, nn_cost, _, _ = nearest_neighbour(graph, depot, others)
        _, to_cost, _, _ = two_opt(graph, depot, others)
        
        assert to_cost <= nn_cost + 1e-6

def test_brute_force_best(graph):
    nodes = list(graph["nodes"].keys())
    nodes.remove("Isolated_Test")
    
    stops = random.sample(nodes, 6)
    depot = stops[0]
    others = stops[1:]
    
    _, to_cost, _, _ = two_opt(graph, depot, others)
    _, bf_cost, _, _ = brute_force(graph, depot, others)
    
    assert bf_cost <= to_cost + 1e-6
