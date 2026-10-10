def bellman_ford(graph, start, end):
    nodes = graph["nodes"]
    edges = graph["edges"]
    
    distances = {n: float('inf') for n in nodes}
    distances[start] = 0
    previous = {n: None for n in nodes}
    
    expanded = 0
    
    V = len(nodes)
    for _ in range(V - 1):
        updated = False
        expanded += 1
        for u in nodes:
            if distances[u] == float('inf'): continue
            for v, edge_data in edges[u].items():
                weight = edge_data["weight"]
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    previous[v] = u
                    updated = True
        if not updated:
            break
            
    if distances[end] == float('inf'):
        return None, float('inf'), expanded
        
    path = []
    curr = end
    while curr:
        path.append(curr)
        curr = previous[curr]
    path.reverse()
    
    return path, distances[end], expanded
