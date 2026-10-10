import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.graph import generate_graph
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from algorithms.bellman_ford import bellman_ford

@pytest.fixture(scope="module")
def graph():
    return generate_graph(filepath=None)

def test_shortest_path_correctness(graph):
    start = "Majestic"
    end = "Electronic City"
    
    path_d, dist_d, exp_d = dijkstra(graph, start, end)
    path_a, dist_a, exp_a = astar(graph, start, end)
    path_b, dist_b, exp_b = bellman_ford(graph, start, end)
    
    assert path_d == path_a == path_b
    assert abs(dist_d - dist_a) < 1e-5
    assert abs(dist_d - dist_b) < 1e-5
    
    # A* should expand fewer or equal nodes compared to Dijkstra
    assert exp_a <= exp_d

def test_unreachable_node(graph):
    start = "Majestic"
    end = "Isolated_Test"
    
    path_d, dist_d, _ = dijkstra(graph, start, end)
    assert path_d is None
    assert dist_d == float('inf')
    
    path_a, dist_a, _ = astar(graph, start, end)
    assert path_a is None
    assert dist_a == float('inf')
