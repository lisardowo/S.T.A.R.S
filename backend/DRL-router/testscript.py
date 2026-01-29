import math
import time
import random
import os
import sys

import torch
import simpy

# Ajusta sys.path para importar módulos del backend
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dijkstra"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "DRL-router"))

from dijk_alg import buildGraphFromConstellation, dijkstra
import router
import satelites
import monitor

def benchmark(num_trials = 1000):
    env = simpy.Environment()
    constellation = satelites.ConstellationManager(env)

    Router = router.IntelligentRouter(constellation, train_mode = False)
    mon = monitor.Monitor()

    for i in range(num_trials):
        
        env.run(until = env.now + 1)

        N_P, N_S = constellation.planes, constellation.sats_per_plane
        src_p, src_s = random.randint(0, N_P-1), random.randint(0, N_S-1)
        dst_p , dst_s = random.randint(0, N_P-1), random.randint(0, N_S-1)
        src_id, dst_id = f"S{src_p}_{src_s}", f"S{dst_p}_{dst_s}"

        ctx_drl = mon.start_tx(env.now, "DRL", src_id, dst_id, size_bytes = 1024)
        candidates, features, adj = Router.find_best_routes(src_p, src_s, dst_p ,dst_s)
        algorithm_cost = float("inf")

        if candidates:
            state_tensor = torch.tensor(features, dtype = torch.float32).to(Router.device)
            adj_tensor = adj.to(Router.device) if adj is not None else None
            with torch.no_grad():
                ratios, _ = Router.agent(state_tensor, adj_tensor, training = False)
            ratios_np = ratios.cpu().numpy()
            best_idx = int(ratios_np.argmax())
            best_route =  candidates[best_idx]
            mon.record_decision_end(ctx_drl)
            algorithm_cost = best_route["delay"]
            for link in best_route["enlaces"]:
                u, v = link.split("-") # or link.split("-")
                m = constellation.get_link_metrics(u , v)
                mon.record_hop(ctx_drl, u , v , m)
        else:
            mon.record_decision_end(ctx_drl)

       
        G = buildGraphFromConstellation(constellation)
        ctx_dij = mon.start_tx(env.now, "Dijkstra",src_id, dst_id, size_bytes=1024)
        path, dij_cost = dijkstra(G, src_id, dst_id)
        mon.record_decision_end(ctx_dij)

        if path:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                m = constellation.get_link_metrics(u, v)
                mon.record_hop(ctx_dij, u , v , m)
            mon.end_tx(env.now,ctx_dij, success = True)
        else:
            mon.end_tx(env.now, ctx_dij, success=False)
        mon.end_tx(env.now, ctx_drl, success = (algorithm_cost < float("inf")), ref_cost=dij_cost, algorithm_cost=algorithm_cost)
    
    print(mon.summary())





def run_test():
    start_time = time.time()
    
    print("-" * 60)
    print("INICIO DE DIAGNÓSTICO DE FORMULAS DE ENRUTAMIENTO SATELITAL - for debug")
    print("-" * 60)

    # 1. Configuración del Escenario (Basado en Iridium según Tabla 1 del documento)
    #[cite: 538]: Iridium tiene 6 planos, 11 satélites por plano.
    N_P = 24  # NumberOfPlanes
    N_S = 66  # NumberOfSatelites
    
    
    N_P, N_S = constellation.planes, constellation.sats_per_plane
    src_p, src_s = random.randint(0, N_P-1), random.randint(0, N_S-1)
    dst_p, dst_s = random.randint(0, N_P-1), random.randint(0, N_S-1)

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
    print("-" * 60) #TODO corregir el testciprt para matchear la version actual del api

if __name__ == "__main__":
    benchmark()
