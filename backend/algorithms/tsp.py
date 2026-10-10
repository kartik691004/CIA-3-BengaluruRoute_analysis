import time
import itertools
from .astar import astar
from .graph import haversine

def precompute_cost_matrix(graph, stops):
    unique_stops = []
    seen = set()
    for s in stops:
        if s not in seen:
            unique_stops.append(s)
            seen.add(s)
    
    n = len(unique_stops)
    matrix = {}
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[(unique_stops[i], unique_stops[j])] = ([unique_stops[i]], 0.0)
            else:
                path, cost, _ = astar(graph, unique_stops[i], unique_stops[j])
                if path is None:
                    raise ValueError(f"No path between {unique_stops[i]} and {unique_stops[j]}")
                matrix[(unique_stops[i], unique_stops[j])] = (path, cost)
                
    return unique_stops, matrix

def nearest_neighbour(graph, depot, stops, matrix=None):
    if matrix is None:
        try:
            unique_stops, matrix = precompute_cost_matrix(graph, [depot] + stops)
        except ValueError as e:
            return None, float('inf'), 0, str(e)
    else:
        unique_stops = [depot] + stops
        
    start_time = time.time()
    
    unvisited = set(unique_stops[1:])
    curr = depot
    
    tour = [depot]
    total_cost = 0.0
    
    while unvisited:
        next_stop = min(unvisited, key=lambda s: matrix[(curr, s)][1])
        total_cost += matrix[(curr, next_stop)][1]
        tour.append(next_stop)
        unvisited.remove(next_stop)
        curr = next_stop
        
    runtime_ms = (time.time() - start_time) * 1000
    
    return tour, total_cost, runtime_ms, matrix

def calculate_tour_cost(tour, matrix):
    return sum(matrix[(tour[i], tour[i+1])][1] for i in range(len(tour)-1))

def two_opt(graph, depot, stops, matrix=None):
    if matrix is None:
        try:
            unique_stops, matrix = precompute_cost_matrix(graph, [depot] + stops)
        except ValueError as e:
            return None, float('inf'), 0, str(e)
            
    tour, nn_cost, _, _ = nearest_neighbour(graph, depot, stops, matrix)
    
    start_time = time.time()
    if tour is None: return None, float('inf'), 0, "No path"
    
    improved = True
    while improved:
        improved = False
        for i in range(1, len(tour) - 1):
            for j in range(i + 1, len(tour)):
                new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                new_cost = calculate_tour_cost(new_tour, matrix)
                
                if new_cost < nn_cost - 1e-6:
                    tour = new_tour
                    nn_cost = new_cost
                    improved = True
                    break
            if improved:
                break
                
    runtime_ms = (time.time() - start_time) * 1000
    return tour, nn_cost, runtime_ms, matrix

def brute_force(graph, depot, stops, matrix=None):
    if matrix is None:
        try:
            unique_stops, matrix = precompute_cost_matrix(graph, [depot] + stops)
        except ValueError as e:
            return None, float('inf'), 0, str(e)
    else:
        unique_stops = [depot] + stops
        
    other_stops = unique_stops[1:]
    if len(other_stops) > 10:
        raise ValueError("N > 10 not supported for brute force")
        
    start_time = time.time()
    best_tour = None
    best_cost = float('inf')
    
    for perm in itertools.permutations(other_stops):
        tour = [depot] + list(perm)
        cost = calculate_tour_cost(tour, matrix)
        if cost < best_cost:
            best_cost = cost
            best_tour = tour
            
    runtime_ms = (time.time() - start_time) * 1000
    return best_tour, best_cost, runtime_ms, matrix
