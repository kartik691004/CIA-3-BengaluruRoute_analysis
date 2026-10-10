import os, sys, time, json, random, tracemalloc, math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
from algorithms.graph import generate_graph, haversine
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from algorithms.bellman_ford import bellman_ford
from algorithms.tsp import precompute_cost_matrix, nearest_neighbour, two_opt, brute_force

def median(lst):
    lst = sorted(lst)
    n = len(lst)
    return lst[n//2] if n % 2 == 1 else (lst[n//2 - 1] + lst[n//2]) / 2.0

def generate_geometric_graph(n_nodes, k=4):
    nodes = {f"N{i}": (random.uniform(12.8, 13.1), random.uniform(77.5, 77.8)) for i in range(n_nodes)}
    edges = {n: {} for n in nodes}
    for n1, p1 in nodes.items():
        sample_nodes = random.sample(list(nodes.items()), min(50, n_nodes))
        dists = [(n2, haversine(p1[0], p1[1], p2[0], p2[1])) for n2, p2 in sample_nodes if n1 != n2]
        dists.sort(key=lambda x: x[1])
        for n2, d in dists[:k]:
            w = d * random.uniform(1.0, 2.5)
            edges[n1][n2] = {"distance_km": d, "weight": w}
            edges[n2][n1] = {"distance_km": d, "weight": w}
    return {"nodes": nodes, "edges": edges}

def run_benchmarks():
    random.seed(42)
    results = {"weight_model": "haversine * uniform(1.0, 2.5)"}
    graph_data = generate_graph(filepath=None)
    nodes = [n for n in graph_data["nodes"] if n != "Isolated_Test"]
    
    results["routing"] = {}
    for n in range(4, 9):
        nn_times, to_times, bf_times, build_times = [], [], [], []
        nn_gaps, to_gaps = [], []
        
        for _ in range(20):
            stops = random.sample(nodes, n)
            t0 = time.time()
            _, matrix = precompute_cost_matrix(graph_data, stops)
            build_times.append((time.time()-t0)*1000)
            
            _, nn_c, nn_t, _ = nearest_neighbour(graph_data, stops[0], stops[1:], matrix=matrix)
            _, to_c, to_t, _ = two_opt(graph_data, stops[0], stops[1:], matrix=matrix)
            _, bf_c, bf_t, _ = brute_force(graph_data, stops[0], stops[1:], matrix=matrix)
            
            nn_times.append(nn_t); to_times.append(to_t); bf_times.append(bf_t)
            if bf_c > 0:
                nn_gaps.append((nn_c - bf_c)/bf_c * 100)
                to_gaps.append((to_c - bf_c)/bf_c * 100)
                
        results["routing"][n] = {
            "build_time_mean": sum(build_times)/20,
            "nn_time_mean": sum(nn_times)/20, "to_time_mean": sum(to_times)/20, "bf_time_mean": sum(bf_times)/20,
            "nn_gap_mean": sum(nn_gaps)/20 if nn_gaps else 0, "nn_gap_max": max(nn_gaps) if nn_gaps else 0,
            "to_gap_mean": sum(to_gaps)/20 if to_gaps else 0, "to_gap_max": max(to_gaps) if to_gaps else 0
        }
        
    for n in [9, 10]:
        stops = random.sample(nodes, n)
        _, matrix = precompute_cost_matrix(graph_data, stops)
        _, _, bf_t, _ = brute_force(graph_data, stops[0], stops[1:], matrix=matrix)
        results["routing"][n] = {"bf_time_single": bf_t}

    d_times_real, a_times_real, d_exp_real, a_exp_real = [], [], [], []
    for _ in range(200):
        start, end = random.sample(nodes, 2)
        t0 = time.time()
        _, cost_d, exp_d = dijkstra(graph_data, start, end)
        d_times_real.append((time.time()-t0)*1000)
        t0 = time.time()
        _, cost_a, exp_a = astar(graph_data, start, end)
        a_times_real.append((time.time()-t0)*1000)
        assert abs(cost_d - cost_a) < 1e-5
        d_exp_real.append(exp_d); a_exp_real.append(exp_a)
        
    mean_d_exp = sum(d_exp_real)/200
    mean_a_exp = sum(a_exp_real)/200
    reduction = ((mean_d_exp - mean_a_exp) / mean_d_exp * 100) if mean_d_exp > 0 else 0
    results["real_graph_200"] = {
        "dijkstra_time": sum(d_times_real)/200, "astar_time": sum(a_times_real)/200,
        "dijkstra_exp": mean_d_exp, "astar_exp": mean_a_exp, "reduction_pct": reduction
    }
    
    sizes = [100, 500, 1000, 5000, 10000]
    results["shortest_path"] = {}
    for size in sizes:
        sgraph = generate_geometric_graph(size)
        snodes = list(sgraph["nodes"].keys())
        d_times, a_times, b_times = [], [], []
        d_exp, a_exp, b_rounds = [], [], []
        d_mem, a_mem, b_mem = [], [], []
        
        for _ in range(10):
            start, end = random.sample(snodes, 2)
            tracemalloc.start()
            t0 = time.time(); _, c_d, e_d = dijkstra(sgraph, start, end); d_times.append((time.time()-t0)*1000)
            _, p_d = tracemalloc.get_traced_memory(); tracemalloc.stop()
            d_exp.append(e_d); d_mem.append(p_d)
            
            tracemalloc.start()
            t0 = time.time(); _, c_a, e_a = astar(sgraph, start, end); a_times.append((time.time()-t0)*1000)
            _, p_a = tracemalloc.get_traced_memory(); tracemalloc.stop()
            a_exp.append(e_a); a_mem.append(p_a)
            assert abs(c_d - c_a) < 1e-5 or (c_d == float('inf') and c_a == float('inf'))
            
            if size <= 1000:
                tracemalloc.start()
                t0 = time.time(); _, c_b, r_b = bellman_ford(sgraph, start, end); b_times.append((time.time()-t0)*1000)
                _, p_b = tracemalloc.get_traced_memory(); tracemalloc.stop()
                b_rounds.append(r_b); b_mem.append(p_b)
                assert abs(c_d - c_b) < 1e-5 or (c_d == float('inf') and c_b == float('inf'))
                
        results["shortest_path"][size] = {
            "dijkstra": {"time": sum(d_times)/10, "exp": sum(d_exp)/10, "mem": sum(d_mem)/10},
            "astar": {"time": sum(a_times)/10, "exp": sum(a_exp)/10, "mem": sum(a_mem)/10}
        }
        if size <= 1000:
            results["shortest_path"][size]["bellman_ford"] = {"time": sum(b_times)/10, "rounds": sum(b_rounds)/10, "mem": sum(b_mem)/10}
            
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    with open("benchmarks/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_benchmarks()
