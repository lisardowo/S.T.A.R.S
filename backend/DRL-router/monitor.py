import matplotlib.pyplot as plt
import os
import networkx as nx

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