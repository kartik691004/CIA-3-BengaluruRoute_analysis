# BengaluruRoute: Video Presentation Script

**[0:00 - 0:30] Introduction**
"Hello, I'm presenting BengaluruRoute, a smart last-mile delivery router built specifically for the urban geography of Bengaluru. Navigating this city means accounting for unpredictable congestion and unstructured road links. The system takes a start depot and a list of requested delivery stops and determines both the shortest driving paths and the most efficient visiting order."

**[0:30 - 1:15] The Prototype and Algorithms**
"As you can see on the interactive Leaflet map, I can select a depot like 'Majestic' and hold Ctrl to select 'Indiranagar' and 'Whitefield'. Under the hood, the backend uses the A* algorithm paired with a Nearest Neighbor and 2-Opt heuristic. We chose A* because it uses a Haversine distance heuristic to pull the search towards the target, expanding far fewer nodes than Dijkstra."

**[1:15 - 2:15] Experimental Results: Shortest Path**
"Looking at the performance benchmarks, A* shows its strength. On a 10,000 node graph, Dijkstra takes 68 milliseconds and expands nearly 5000 nodes. A* takes only 38 milliseconds, examining just 718 nodes. The heuristic strictly underestimates the real cost to guarantee the shortest path, though heavy traffic variability slightly blunts its aggressiveness."

**[2:15 - 3:15] Experimental Results: TSP Ordering**
"For the delivery order, solving it exactly is factorial. At 8 stops, Brute force takes 7 milliseconds. At 10 stops, it spikes to nearly 600 milliseconds. Instead, our 2-Opt solver runs in just 0.05 milliseconds and yields routes that are, on average, within 1.3% of the absolute optimal cost. We get near-perfection instantly."

**[3:15 - 4:00] Conclusion & Application**
"Through rigorous unit testing, including unreachable node safeguards, we've validated the prototype. This exact logic forms the backbone of platforms like Swiggy and Amazon Logistics, proving that heuristic optimization provides the practical scalability required to keep our supply chains moving."
