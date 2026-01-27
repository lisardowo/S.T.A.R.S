import matplotlib.pyplot as plt
import os
import networkx as nx

from collections import defaultdict
import time


def percentile(data, p):
    if not data:
        return 0.0
    s = sorted(data)
    k = int(round((p/100.0) * (len(s)-1)))
    return s[k]

class TrainingMonitoring:
    def plot_training_results(epochs, rewards, throughputs):
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Eje para la Recompensa
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Reward', color='tab:blue')
    ax1.plot(epochs, rewards, color='tab:blue', label='Reward')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Eje para el Throughput
    ax2 = ax1.twinx()
    ax2.set_ylabel('Avg Throughput', color='tab:red')
    ax2.plot(epochs, throughputs, color='tab:red', linestyle='--', label='Throughput')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title('Progreso del Entrenamiento DRL')
    fig.tight_layout()
    plt.show()

    

def log_epoch_stats(file_path, data):
    """
    Registra las estadísticas de la época en un archivo de texto.
    Data debe ser un diccionario con las llaves correspondientes.
    """
    file_exists = os.path.isfile(file_path)
    
    with open(file_path, "a") as f:
        # Escribir cabecera si el archivo es nuevo
        if not file_exists:
            header = ("Epoch\tReward\tBest?\tAvg_TP\tAvg_Delay\tSrc\tDst\t"
                     "Ratios(W/E/S)\tMax_Load\tExecution_Time\n")
            f.write(header)
        
        # Formatear los datos en columnas
        line = (
            f"{data['epoch']}\t"
            f"{data['reward']:.4f}\t"
            f"{'[NUEVO MEJOR]' if data['is_best'] else '-'}\t"
            f"{data['tp']:.2f}\t"
            f"{data['delay']:.4f}\t"
            f"{data['src']}\t"
            f"{data['dst']}\t"
            f"{data['ratios']}\t"
            f"{data['max_load']:.2f}\t"
            f"{data['exec_time']:.4f}\n"
        )
        f.write(line)

def visualize_satellite_routes(candidates, n_planes, n_sats, src, dst):
    """
    Dibuja la malla de satélites y resalta las rutas candidatas.
    """
    G = nx.Graph()
    pos = {}

    # 1. Crear la malla completa de la constelación
    for p in range(n_planes):
        for s in range(n_sats):
            node_id = f"S{p}_{s}"
            G.add_node(node_id)
            pos[node_id] = (p, s) # Posición tipo grid

    # 2. Dibujar todos los nodos y conexiones tenues de fondo
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color='lightgrey', alpha=0.5)
    
    # 3. Resaltar las rutas candidatas con distintos colores
    colors = ['#FF5733', '#33FF57', '#3357FF'] # Naranja, Verde, Azul
    for i, cand in enumerate(candidates):
        path_edges = []
        for enlace in cand['enlaces']:
            u, v = enlace.split('-')
            path_edges.append((u, v))
        
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                               edge_color=colors[i % len(colors)], 
                               width=2, label=f"Ruta {i+1}: {cand['estrategia']}")

    # 4. Marcar Origen y Destino
    nx.draw_networkx_nodes(G, pos, nodelist=[src, dst], node_size=200, node_color='yellow', edgecolors='black')
    
    plt.title(f"Topología GNN: Rutas de {src} a {dst}")
    plt.xlabel("Planos Orbitales")
    plt.ylabel("Satélites por Plano")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.show()

class Monitor:
    def __init__(self):
        self.tx = []
        self.counters = defaultdict(int)
        self.hist = defaultdict(list)
    

    def start_tx (self, env_now, algorithm, src, dst, size_bytes):
        ctx = {
            "algorithm" : algorithm
            "src" : src, "dst" : dst,
            "size" : size_bytes,
            "start" : env_now
            "decision_ms" : #TODO agregar tiempo de decision
            "hops" : [],
            "hop_metrics" : [],
            "succes" :  #TODO agregar status succes
        }
        ctx["t_decision_start_ns"] = time.perf_counter_ns()
        return ctx
    
    def record_decision_end(self, ctx):
        t0 = ctx.pop("t_decision_start_ns", None)
        if t0 is not None:
            ctx["decision_ms"] = (time.perf_counter_ns() - t0) /1e6
    
    def record_hop(self, ctx, u, v, metrics):
        ctx["hops"].append((u,v))
        ctx["hop_metrics"].append(metrics or {})
        self.hist["q_delay"].append((metrics or {}).get("q_delay", 0.0))
        self.hist["r_delay"].append((metrics or {}).get("r_delay", 0.0))
        self.hist["distance"].append((metrics or {}).get("distance", 0.0))
        self.hist["throughput"].append((metrics or {}).get("link_thorughput", 0.0))
    
    def end_tx(self, env_now, ctx, success, ref_cost = None, algorithm_cost = None):
        ctx["end"] = env_now
        ctx[succes] = success
        ctx["e2e_latency"] = env_now - ctx["start"]
        ctx["hop_count"] = len(ctx["hops"])
        if ref_cost is not None and algorithm_cost is not None and ref_cost > 0:
            ctx["path_stretch"] = algorithm_cost/ref_cost
        self.tx.append(ctx)
        self.counters[f"{tx_ctx['algo']}_total"] += 1
        self.counters[f"{tx_ctx['algo']}_success"] += int(success)

    def summary(self):
        out = {"per_algorithm" : {}}
        algorithms = {t["algorithm"] for t in self.tx}
        for algorithm in algorithms:
            e2e = [t["e2e_latency"] for t in self.tx if t["algorithm"] == algorithm]
            hops = [t["hop_count"] for t in self.tx if t["algorithm"] == algorithm]
            decs = [t["decision_ms"] for t in self.tx if t["algorithm"] == algorithm]
            stretches = [t.get("path_stretch") for t in self.tx if t["algorithm"] == algorithm]
            succ = self.counters.get(f"{algorithm}_succes", 0)
            tot = self.counters.get(f"{algorithm}_total", 0)
            out["per_algorithm"][algorithm] = {
                "e2e_avg" : sum(e2e)/len(e2e) if e2e else 0.0,
                "e2e_p95" : percentile(e2e, 95);
                "hop_avg" : sum(hops)/len(hops) if hops else 0.0,
                "decision_ms_avg" : sum(decs)/len(decs) if decs else 0.0,
                "path_stretch_avg" : sum(stretches) /len(stretches) if stretches else None,
                "success_rate" : succ /max(tot, 1)
            }
        return out