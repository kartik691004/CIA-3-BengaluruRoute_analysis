import heapq

def dijkstra(graph, start, end):
    nodes = graph["nodes"]
    edges = graph["edges"]
    
    pq = [(0, start)]
    distances = {n: float('inf') for n in nodes}
    distances[start] = 0
    previous = {n: None for n in nodes}
    expanded = 0
    
    while pq:
        curr_dist, curr_node = heapq.heappop(pq)
        
        if curr_dist > distances[curr_node]:
            continue
            
        expanded += 1
            
        if curr_node == end:
            break
            
        for neighbor, edge_data in edges[curr_node].items():
            weight = edge_data["weight"]
            dist = curr_dist + weight
            
            if dist < distances[neighbor]:
                distances[neighbor] = dist
                previous[neighbor] = curr_node
                heapq.heappush(pq, (dist, neighbor))
                
    if distances[end] == float('inf'):
        return None, float('inf'), expanded
        
    path = []
    curr = end
    while curr:
        path.append(curr)
        curr = previous[curr]
    path.reverse()
    
    return path, distances[end], expanded
