import math
import time
import networkx as nx
import matplotlib.pyplot as plt
import formulas  

def run_test():
    start_time = time.time()
    
    print("-" * 60)
    print("INICIO DE DIAGNÓSTICO DE FORMULAS DE ENRUTAMIENTO SATELITAL - for debug")
    print("-" * 60)

    # 1. Configuración del Escenario (Basado en Iridium según Tabla 1 del documento)
    #[cite: 538]: Iridium tiene 6 planos, 11 satélites por plano.
    N_P = 6  # NumberOfPlanes
    N_S = 11  # NumberOfSatelites
    
    # Definimos Nodo Origen (Plano 0, Satélite 0) y Destino (Plano 3, Satélite 5)
    src_plane, src_sat = 0, 0
    dst_plane, dst_sat = 3, 5

    print(f"[*] Configuración de Constelación:")
    print(f"    - Planos (N_P): {N_P}")
    print(f"    - Satélites por plano (N_S): {N_S}")
    print(f"    - Nodo Origen: P{src_plane}/S{src_sat}")
    print(f"    - Nodo Destino: P{dst_plane}/S{dst_sat}")
    print("-" * 60)

    # 2. Conversión de índices discretos a ángulos (Física del problema)
    # RAAN varía de 0 a 2pi entre planos. Phase varía de 0 a 2pi dentro del plano.
    src_raan = src_plane * (2 * math.pi / N_P)
    dst_raan = dst_plane * (2 * math.pi / N_P)
    
    # Simulación de fase (latitud argumental aproximada para la prueba)
    src_lat = src_sat * (2 * math.pi / N_S)
    dst_lat = dst_sat * (2 * math.pi / N_S)

    # 3. Probando Fórmulas Paso a Paso
    
    # A. RAAN Delta [cite: 244]
    raan_delta = formulas.RAAN_Delta(src_raan, dst_raan)
    print(f"[1] RAAN Delta calculado: {raan_delta:.4f} rad")

    # B. Saltos Este/Oeste [cite: 252, 253]
    # Nota: phaseDelta en tu archivo calcula la diferencia de fase entre planos adyacentes (Eq 9)
    # Pero eastANDwest_Hops usa Omega_Delta interno.
    hops_h = formulas.eastANDwest_Hops(raan_delta, N_P)
    print(f"[2] Saltos Horizontales (Inter-plano):")
    print(f"    - West Hops: {hops_h['west']}")
    print(f"    - East Hops: {hops_h['east']}")

    # C. Normalización de Ángulo de Fase [cite: 264-267]
    # Necesitamos el phase_delta (diferencia de fase entre satélites vecinos en planos adyacentes)
    # Asumiremos phase index 1 para obtener la constante delta
    p_delta = formulas.phaseDelta(N_S, N_P, 1) 
    
    east_lat_delta, west_lat_delta = formulas.phaseAngleNormalization(
        dst_lat, src_lat, hops_h['east'], hops_h['west'], p_delta
    )
    print(f"[3] Delta de Latitud Normalizada:")
    print(f"    - Vía Este: {east_lat_delta:.4f} rad")
    print(f"    - Vía Oeste: {west_lat_delta:.4f} rad")

    # D. Saltos Cardinales (Intra-plano/Verticales) [cite: 271-274]
    hops_v = formulas.CardinalDirectionsHops(east_lat_delta, west_lat_delta, N_S)
    print(f"[4] Saltos Verticales Calculados (Intra-plano):")
    for k, v in hops_v.items():
        print(f"    - {k}: {v}")

    # E. Conteo Mínimo de Saltos [cite: 285]
    try:
        min_total_hops = formulas.GetOptimalPaths(src_sat, src_plane, hops_h, hops_v, NumberSatelites=N_S, NumberPlanes=N_P) #TODO Modificar los argumentos -- Github Issues --
        print(f"[5] TOTAL Mínimo de saltos requeridos (Hop Count): {min_total_hops}")
    except Exception as e:
        print(f"[!] Error en GetOptimalPaths: {e}")
        print("    (Consejo: Revisa que 'GetOptimalPaths' retorne un int, no un objeto lambda)")
        return

    execution_time = time.time() - start_time
    print("-" * 60)
    print(f"[*] Ejecución numérica completada en {execution_time:.6f} segundos")
    print("-" * 60)
"""1ara resaltarla
    # Esto es una reconstrucción lógica basada en los resultados de tus fórmulas
    # Calculamos el costo de las 4 opciones posibles
    paths_costs = {
        'West + NW': h_hops['west'] + v_hops['north_west'],
        'West + SW': h_hops['west'] + v_hops['south_west'],
        'East + NE': h_hops['east'] + v_hops['north_east'],
        'East + SE': h_hops['east'] + v_hops['south_east']
    }
    
    best_strategy = formulas.GetOptimalPaths(h_hops, v_hops, SubOptimalPaths=3)[0]
    print(f"[*] Estrategia ganadora para visualización: {best_strategy}")

    # Lógica simple para dibujar el camino (Pathfinding simulado basado en la estrategia)
    path_nodes = [(src_p, src_s)]
    curr_p, curr_s = src_p, src_s
    
    # Decodificar estrategia
    direction = best_strategy.split(' + ')
    h_dir = direction[0] # West o East
    v_dir = direction[1] # NW, SW, NE, SE
    
    # 1. Moverse horizontalmente
    steps_h = h_hops['west'] if h_dir == 'West' else h_hops['east']
    for _ in range(steps_h):
        if h_dir == 'West':
            curr_p = (curr_p - 1) % N_P
        else:
            curr_p = (curr_p + 1) % N_P
        path_nodes.append((curr_p, curr_s))
        
    # 2. Moverse verticalmente
    # Nota: NW implica moverse al norte en satélites. SW al sur.
    steps_v = 0
    if v_dir == 'NW': steps_v = v_hops['north_west']
    elif v_dir == 'SW': steps_v = v_hops['south_west']
    elif v_dir == 'NE': steps_v = v_hops['north_east']
    elif v_dir == 'SE': steps_v = v_hops['south_east']
    
    # Dirección vertical: Asumimos índices crecientes van al "Norte" (o Sur dependiendo convención)
    # En grafos grid, y+1 es "arriba".
    vertical_step = 1 if 'N' in v_dir else -1 # Simplificación visual
    
    for _ in range(steps_v):
        curr_s = (curr_s + vertical_step) % N_S
        path_nodes.append((curr_p, curr_s))

    # Dibujar Camino
    path_edges = list(zip(path_nodes, path_nodes[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='gold', width=3)
    nx.draw_networkx_nodes(G, pos, nodelist=path_nodes, node_color='yellow', node_size=100)

    # Dibujar Origen y Destino
    nx.draw_networkx_nodes(G, pos, nodelist=[(src_p, src_s)], node_color='green', label='Source', node_size=500)
    nx.draw_networkx_nodes(G, pos, nodelist=[(dst_p, dst_s)], node_color='red', label='Dest', node_size=500)

    # Etiquetas
    labels = {node: f"{node}" for node in G.nodes() if node in path_nodes or node == (src_p, src_s) or node == (dst_p, dst_s)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

    plt.title(f"Visualización de Ruta Satelital (Estrategia: {best_strategy})")
    plt.xlabel("Planos Orbitales (Inter-plane)")
    plt.ylabel("Satélites en Plano (Intra-plane)")
    plt.legend(["Nodos", "Enlaces", "Ruta", "Saltos", "Origen", "Destino"])
    plt.grid(True, linestyle='--', alpha=0.5)
    
    print("[*] Gráfico generado. Cerrar ventana para terminar.")
    plt.show()

if __name__ == "__main__":
    run_test()
#- ---- -- -- -- Debug code for formulas.py here - ---- -- -- --

"""
run_test()