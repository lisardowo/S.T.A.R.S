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

    adj = {}

    for p in range(constellation.planes):
        for s in range(constellation.sats_perplane):
            u = f"S{p}_{s}"
            adj[u] = []
            for ds in (-1, 1):
                ns = s(s + ds) % constellation.sats_per_plane
                v = f"S{p}_{ns}"
                m = constellation.get_link_metrics(u, v)
                w = m.get("delay", 1.0)
                adj[u].append(Edge(w,v))
            np = (p + 1) % constellation.planes
            v = f"S{np}_{s}"
            m = constellation.get_link_metrics(u, v)
            w = m.get("delay", 1.0)
            adj[u].append(Edge(w, v))



def dijkstra(graph, start, end):
    previous = {v: None for v in graph.adjacency_list.keys()}
    visited = {v: False for v in graph.adjacency_list.keys()}
    distances = {v: float("inf") for v in graph.adjacency_list.keys()}
    distances[start] = 0
    queue = PriorityQueue()
    queue.add_task(0, start)
    path = []
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




def visualize_graph(graph, vertices, start_node, end_node, shortest_path=None):
    """
    Visualiza el grafo con NetworkX y resalta el camino más corto si existe
    """
    # Crear grafo dirigido de NetworkX
    G = nx.DiGraph()
   
    # Agregar nodos
    for vertex in vertices.values():
        G.add_node(vertex.value)
   
    # Agregar aristas con pesos
    edge_labels = {}
    for vertex, edges in graph.adjacency_list.items():
        for edge in edges:
            G.add_edge(vertex.value, edge.vertex.value, weight=edge.distance)
            edge_labels[(vertex.value, edge.vertex.value)] = f'{edge.distance:.2f}'
   
    # Configurar el layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
   
    # Crear figura
    plt.figure(figsize=(14, 10))
   
    # Dibujar todos los nodos
    node_colors = []
    for node in G.nodes():
        if node == start_node:
            node_colors.append('#90EE90')  # Verde claro para inicio
        elif node == end_node:
            node_colors.append('#FFB6C6')  # Rosa claro para fin
        elif shortest_path and node in shortest_path:
            node_colors.append('#FFD700')  # Dorado para nodos en el camino
        else:
            node_colors.append('#87CEEB')  # Azul cielo para otros
   
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=800, alpha=0.9)
   
    # Dibujar aristas
    if shortest_path:
        # Aristas del camino más corto
        path_edges = [(shortest_path[i], shortest_path[i+1])
                      for i in range(len(shortest_path)-1)]
       
        # Dibujar aristas normales
        normal_edges = [e for e in G.edges() if e not in path_edges]
        nx.draw_networkx_edges(G, pos, edgelist=normal_edges,
                              edge_color='gray', alpha=0.5,
                              arrows=True, arrowsize=20, width=1.5)
       
        # Dibujar aristas del camino más corto
        nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                              edge_color='red', alpha=0.8,
                              arrows=True, arrowsize=25, width=3)
    else:
        nx.draw_networkx_edges(G, pos, edge_color='gray',
                              alpha=0.5, arrows=True,
                              arrowsize=20, width=1.5)
   
    # Dibujar etiquetas de nodos
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
   
    # Dibujar pesos de aristas
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
   
    # Título y leyenda
    if shortest_path:
        plt.title(f'Grafo con camino más corto de {start_node} a {end_node}\n'
                 f'Camino: {" → ".join(shortest_path)}',
                 fontsize=14, fontweight='bold')
    else:
        plt.title(f'Grafo generado aleatoriamente',
                 fontsize=14, fontweight='bold')
   
    plt.axis('off')
    plt.tight_layout()
    plt.show()


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