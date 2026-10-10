from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from algorithms.graph import generate_graph
from algorithms.tsp import nearest_neighbour, two_opt, brute_force

app = FastAPI()
# NOTE: no filepath here. Vercel (and most serverless hosts) mount the function
# bundle read-only, so writing graph.json at import time crashed the whole app
# with FUNCTION_INVOCATION_FAILED on every request. The graph is deterministic
# (random.seed(42)), so it only ever needs to live in memory.
graph_data = generate_graph(filepath=None)

class RouteRequest(BaseModel):
    depot: str
    stops: list[str]
    algorithm: str

@app.get("/graph")
def get_graph():
    return graph_data

@app.post("/route")
def compute_route(req: RouteRequest):
    if req.depot == "Isolated_Test" or "Isolated_Test" in req.stops:
        raise HTTPException(status_code=400, detail="Node 'Isolated_Test' is unreachable. Please select different stops.")
        
    def process_algo(algo):
        if algo == "nearest_neighbour":
            tour, cost, time_ms, matrix = nearest_neighbour(graph_data, req.depot, req.stops)
        elif algo == "two_opt":
            tour, cost, time_ms, matrix = two_opt(graph_data, req.depot, req.stops)
        elif algo == "brute_force":
            if len(req.stops) > 8:
                raise HTTPException(status_code=400, detail="Brute force not supported for N > 8")
            tour, cost, time_ms, matrix = brute_force(graph_data, req.depot, req.stops)
        else:
            raise HTTPException(status_code=400, detail="Unknown algorithm")
            
        if tour is None:
            raise HTTPException(status_code=400, detail="Path not found")
            
        path_details = []
        total_km = 0
        for i in range(len(tour)-1):
            p, c = matrix[(tour[i], tour[i+1])]
            leg_km = 0
            for j in range(len(p)-1):
                leg_km += graph_data["edges"][p[j]][p[j+1]]["distance_km"]
            total_km += leg_km
            path_details.append({"from": tour[i], "to": tour[i+1], "path": p, "cost": c, "distance_km": leg_km})
            
        # Our A* uses straight line heuristics. Actual nodes expanded is not natively bubbled up from TSP precomputation easily without refactoring tsp.py. We'll return N/A for TSP.
        est_minutes = cost * 2.5 
        
        return {
            "algorithm": algo,
            "tour": tour,
            "cost": cost,
            "distance_km": total_km,
            "estimated_minutes": est_minutes,
            "runtime_ms": time_ms,
            "nodes_expanded": "N/A (Precomputed)",
            "path_details": path_details
        }

    if req.algorithm == "all":
        results = {}
        for algo in ["nearest_neighbour", "two_opt"]:
            results[algo] = process_algo(algo)
        if len(req.stops) <= 8:
            results["brute_force"] = process_algo("brute_force")
        return {"compare": True, "results": results}
    else:
        res = process_algo(req.algorithm)
        res["compare"] = False
        return res

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()