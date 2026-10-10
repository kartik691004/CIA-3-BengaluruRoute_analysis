# BengaluruRoute: Smart Last-Mile Delivery Router

## 1. Problem, Inputs, Outputs, and Chosen Algorithm
**Problem Statement:** Last-mile delivery in Bengaluru requires navigating an extremely congested urban environment to serve multiple stops efficiently. The system must find the shortest time/distance paths on the road network and optimize the order of these stops (a TSP problem).
**Inputs:** A sparse urban road graph of 41 nodes (major landmarks) connected by weighted edges (Weight Model: `haversine * uniform(1.0, 2.5)`). The user inputs a starting depot and a subset of stops.
**Outputs:** An ordered routing tour (Note: this is an **Open Tour**, meaning it ends at the last stop and does not mandate a return trip to the depot), total cost (estimated congestion distance), total runtime in ms, nodes expanded, and the detailed point-to-point sequence.
**Chosen Algorithm:** A* heuristic search for shortest-paths (leg segments) paired with a Nearest Neighbor initial ordering + 2-Opt swap improvement phase for the multi-stop TSP optimization.

## 2. Prototype and Test Cases
The prototype is a Python 3.11 + FastAPI application exposing `/route` and `/graph` endpoints, alongside a static Leaflet.js map on the frontend for interaction. 

Pytest test cases verified:
1. Shortest paths between Dijkstra, A*, and Bellman-Ford matched exactly.
2. A single unreachable node (`Isolated_Test`) accurately returns a 400 error.
3. Node deduplication is appropriately handled in the cost matrix build.
4. 2-opt correctly guarantees an equal or cheaper route compared to NN without regressing.
5. The `all` comparison endpoint explicitly returns exact algorithm hierarchies (`brute_force <= two_opt <= nearest_neighbour`).

## 3. Why A* and NN+2-Opt?
- **A* vs Dijkstra / Bellman-Ford:** A* effectively points the search towards the destination using the Haversine line-of-sight heuristic. Bellman-Ford checks every edge $V$ times and is prohibitively slow for typical road networks.
- **NN+2-Opt vs Brute Force:** Brute force evaluates $O(N!)$ combinations, ensuring optimality. But at $N=10$, calculation time explodes. NN provides a rapid greedy baseline, and 2-Opt systematically untangles "crossed paths".

## 4. Complexity and Experimental Results

### Dijkstra vs A* (Real 41-Node Graph, 200 Pairs)
| Algorithm | Mean Time (ms) | Mean Nodes Expanded |
| --- | --- | --- |
| Dijkstra | 0.034 ms | 20.75 |
| A* | 0.042 ms | 10.30 |
**Reduction in Expanded Nodes:** **50.37%**

### Shortest Path Benchmark (Synthetic Geometric Graphs)
| Nodes | Dijkstra Time / Exp | A* Time / Exp | Bellman-Ford Time / Rounds |
| --- | --- | --- | --- |
| 100 | 0.26ms / 48.3 | 0.42ms / 25.7 | 1.70ms / 7.5 |
| 500 | 1.54ms / 205.9 | 2.11ms / 66.4 | 17.59ms / 8.2 |
| 1000 | 4.07ms / 430.8 | 4.13ms / 128.4 | 41.74ms / 8.8 |
| 5000 | 23.83ms / 1908.1 | 18.87ms / 402.2 | N/A |
| 10000 | 71.35ms / 5423.0 | 59.25ms / 1368.5 | N/A |

*Note: A* expands significantly fewer nodes (e.g., 1368 vs 5423 at 10,000 nodes) which drastically cuts runtime as the graph scales. Because the traffic factor reaches up to 2.5x, the heuristic is often an underestimation, which provides more modest gains at smaller scale but proves vital at N=10000.*

### Routing TSP Benchmark (Bengaluru Graph, 20 repeats)
| N Stops | Matrix Build | NN Mean | 2-Opt Mean | BF Mean | 2-Opt Mean Gap | 2-Opt Max Gap |
| --- | --- | --- | --- | --- | --- | --- |
| **4** | 0.59 ms | 0.005 ms | 0.008 ms | 0.008 ms | 0.11% | 2.23% |
| **5** | 0.89 ms | 0.006 ms | 0.015 ms | 0.029 ms | 1.69% | 16.33% |
| **6** | 1.29 ms | 0.008 ms | 0.029 ms | 0.149 ms | 1.16% | 12.57% |
| **7** | 1.80 ms | 0.009 ms | 0.042 ms | 0.995 ms | 2.43% | 21.94% |
| **8** | 2.46 ms | 0.013 ms | 0.078 ms | 7.326 ms | 1.31% | 9.80% |

At $N=9$, Brute Force spikes to 63.5ms, and at $N=10$, it spikes to 605ms. 2-Opt operates in microseconds while keeping the optimality gap generally below 2.5%.

## 5. Practical Applications
This system directly mirrors logistics orchestration software used by companies like Swiggy, Dunzo, and Amazon Logistics. Beyond parcel delivery, this architecture scales to municipal garbage collection routing, school bus route coordination, and emergency vehicle dispatching.
