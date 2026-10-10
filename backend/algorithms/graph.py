import os
import json
import math
import random

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_graph(filepath="data/graph.json"):
    nodes = {
        "Majestic": (12.9766, 77.5713),
        "Indiranagar": (12.9719, 77.6412),
        "Koramangala": (12.9279, 77.6271),
        "Whitefield": (12.9698, 77.7499),
        "Electronic City": (12.8452, 77.6602),
        "Hebbal": (13.0354, 77.5988),
        "Jayanagar": (12.9299, 77.5824),
        "Yelahanka": (13.1007, 77.5963),
        "Marathahalli": (12.9569, 77.7011),
        "HSR Layout": (12.9121, 77.6446),
        "BTM Layout": (12.9166, 77.6101),
        "Malleshwaram": (13.0031, 77.5710),
        "Banashankari": (12.9152, 77.5736),
        "JP Nagar": (12.9063, 77.5857),
        "Bannerghatta Road": (12.8988, 77.5996),
        "CHRIST University Hosur Rd": (12.9345, 77.6059),
        "KR Puram": (13.0084, 77.6953),
        "Silk Board": (12.9176, 77.6238),
        "Yeshwanthpur": (13.0279, 77.5409),
        "Basavanagudi": (12.9421, 77.5750),
        "Domlur": (12.9609, 77.6387),
        "Ulsoor": (12.9782, 77.6247),
        "Shivajinagar": (12.9868, 77.6041),
        "Madiwala": (12.9226, 77.6174),
        "Bellandur": (12.9304, 77.6784),
        "Sarjapur Road": (12.9127, 77.6653),
        "Kalyan Nagar": (13.0280, 77.6399),
        "Kammanahalli": (13.0117, 77.6385),
        "RT Nagar": (13.0238, 77.5947),
        "Sanjaynagar": (13.0353, 77.5804),
        "Peenya": (13.0329, 77.5274),
        "Rajajinagar": (12.9982, 77.5530),
        "Vijayanagar": (12.9716, 77.5273),
        "Kengeri": (12.9030, 77.4811),
        "Nagarbhavi": (12.9669, 77.5118),
        "RR Nagar": (12.9260, 77.5174),
        "Padmanabhanagar": (12.9163, 77.5583),
        "Nayandahalli": (12.9413, 77.5280),
        "Bommanahalli": (12.9048, 77.6253),
        "Kudlu Gate": (12.8931, 77.6438),
        "Isolated_Test": (12.0, 77.0) 
    }
    
    random.seed(42)
    edges = {n: {} for n in nodes}
    
    k = 4
    for n1, p1 in nodes.items():
        if n1 == "Isolated_Test": continue
        
        dists = []
        for n2, p2 in nodes.items():
            if n2 != n1 and n2 != "Isolated_Test":
                dists.append((n2, haversine(p1[0], p1[1], p2[0], p2[1])))
        
        dists.sort(key=lambda x: x[1])
        for n2, d in dists[:k]:
            traffic_factor = random.uniform(1.0, 2.5)
            w = d * traffic_factor
            
            assert w >= d, "Weight must be >= haversine for A* admissibility"
            
            edges[n1][n2] = {"distance_km": d, "weight": w}
            edges[n2][n1] = {"distance_km": d, "weight": w}
            
    highways = [("Silk Board", "Electronic City"), ("Majestic", "Yeshwanthpur"), ("Indiranagar", "KR Puram")]
    for h1, h2 in highways:
        if h1 in nodes and h2 in nodes:
            d = haversine(nodes[h1][0], nodes[h1][1], nodes[h2][0], nodes[h2][1])
            traffic_factor = random.uniform(1.0, 1.2)
            w = d * traffic_factor
            assert w >= d
            edges[h1][h2] = {"distance_km": d, "weight": w}
            edges[h2][h1] = {"distance_km": d, "weight": w}
            
    data = {"nodes": nodes, "edges": edges}
    
    if filepath:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    return data