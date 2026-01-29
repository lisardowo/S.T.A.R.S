import itertools
from heapq import heappush, heappop
from random import randint, uniform, choice
import networkx as nx
import matplotlib.pyplot as plt


class Graph:
    def __init__(self, adjacency_list):
        self.adjacency_list = adjacency_list

class Edge:
    def __init__(self, distance, vertex):
        self.distance = distance
        self.vertex = vertex

class Vertex:
    def __init__(self, value):
        self.value = value

class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def __len__(self):
        return len(self.pq)

    def add_task(self, priority, task):
        if task in self.entry_finder:
            self.update_priority(priority, task)
            return self
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heappush(self.pq, entry)

    def update_priority(self, priority, task):
        entry = self.entry_finder[task]
        count = next(self.counter)
        entry[0], entry[1] = priority, count

    def pop_task(self):
        while self.pq:
            priority, count, task = heappop(self.pq)
            del self.entry_finder[task]
            return priority, task
        raise KeyError('pop from an empty priority queue')
   

def buildGraphFromConstellation(constellation):

    G = nx.DiGraph()

    for p in range(constellation.planes):
        for s in range(constellation.sats_per_plane):
            u = f"S{p}_{s}"
            G.add_node(u)
            
            for ds in (-1, 1):
                ns = (s + ds) % constellation.sats_per_plane
                v = f"S{p}_{ns}"
                m = constellation.get_link_metrics(u, v)
                w = m.get("delay", 1.0)
                G.add_edge(u, v, weight = w)

            np = (p + 1) % constellation.planes
            v = f"S{np}_{s}"
            m = constellation.get_link_metrics(u, v)
            w = m.get("delay", 1.0)
            G.add_edge(u, v , weight = w)

    return G



def dijkstra(graph, start, end):
    try:
        path = nx.dijkstra_path(graph, source = start, target = end, weight = "weight")
        cost = nx.dijkstra_path_length(graph, source = start, target = end, weight = "weight")
        return path,cost 
    except nx.NetworkXNoPath:
        return None, float("inf")
    previous = {v: None for v in graph.adjacency_list.keys()}
    visited = {v: False for v in graph.adjacency_list.keys()}
    distances = {v: float("inf") for v in graph.adjacency_list.keys()}
    distances[start] = 0
    queue = PriorityQueue()
    queue.add_task(0, start)

    while queue:
        removed_distance, removed = queue.pop_task()
        visited[removed] = True

        if removed is end:
            while previous[removed]:
                path.append(removed.value)
                removed = previous[removed]
            path.append(start.value)
            print(f"shortest distance to {end.value}: ", distances[end])
            print(f"path to {end.value}: ", path[::-1])
            return path[::-1], distances[end]

        for edge in graph.adjacency_list[removed]:
            if visited[edge.vertex]:
                continue
            new_distance = removed_distance + edge.distance
            if new_distance < distances[edge.vertex]:
                distances[edge.vertex] = new_distance
                previous[edge.vertex] = removed
                queue.add_task(new_distance, edge.vertex)
    return None, None


#Test Snippet

if __name__ == "__main__":

    NUMBER_NODES = 10
    LOWER = 0.1
    UPPER = 2

    nodes = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    number_edges_nodes = [randint(1, NUMBER_NODES // 2) for _ in nodes]
    print(number_edges_nodes)
    vertices = {name: Vertex(name) for name in nodes}
    adj_list = {}

    for i, num_edges in enumerate(number_edges_nodes):
        edges = []
        for _ in range(num_edges):
            target = choice(nodes)
            #if nodes[i] == target: continue ; num_edges += 1
            edges.append(
                Edge(uniform(LOWER, UPPER), vertices[target])
            )
        adj_list[vertices[nodes[i]]] = edges

    my_graph = Graph(adj_list)

    # Parte para controlar (start, end)

    start_vertex = vertices[nodes[0]]
    end_vertex = vertices[nodes[8]]
    shortest_path, distance = dijkstra(my_graph, start=start_vertex, end=end_vertex)

    visualize_graph(my_graph, vertices, nodes[0], nodes[9], shortest_path)