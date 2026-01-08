import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "DRL-router"))

import simpy
import time
import torch
import json

from satelites import ConstellationManager
from router import IntelligentRouter

# Importamos el módulo compilado de C++ (asumiendo que se llama cpp_core)
try:
    import cpp_core
except ImportError:
    print("[!] Error: No se encontró el módulo 'cpp_core'. Asegurate de compilar el binding.")
    # Mock para que el código no falle si no has compilado aún
    class MockCpp:
        def compress(self, d): return d
        def fragment(self, d, s): return [d[i:i+s] for i in range(0, len(d), s)]
    cpp_core = MockCpp()

class TransmissionSimulator:
    def __init__(self, env, constellation, router):
        self.env = env
        self.constellation = constellation
        self.router = router
        self.transmission_log = [] # Aquí guardaremos todo para el Frontend

    def process_and_send(self, raw_data_str, src_p, src_s, dst_p, dst_s):
        """
        Flujo principal: Comprime -> Fragmenta -> DRL Routing -> Simula Envío
        """
        print(f"\n[*] Iniciando transmisión de {len(raw_data_str)} bytes...")
        
        # 1. PROCESAMIENTO HIBRIDO (C++)
        # Convertir string a bytes
        raw_bytes = raw_data_str.encode('utf-8')
        original_size = len(raw_bytes)
        
        t0 = time.time()
        compressed = cpp_core.compress(raw_bytes)
        # Fragmentar (ej. 1024 bytes por paquete para la simulación)
        fragments = cpp_core.fragment(compressed, 1024) 
        proc_time = (time.time() - t0) * 1000 # ms
        
        print(f"    -> Comprimido: {len(compressed)} bytes. Fragmentos: {len(fragments)}")

        # 2. SELECCIÓN DE RUTAS (DRL - Python)
        candidates, features, adj = self.router.find_best_routes(src_p, src_s, dst_p, dst_s)
        
        if not candidates:
            return {"status": "FAILED", "reason": "No routes found"}

        # Obtener ratios del modelo
        state_tensor = torch.tensor(features, dtype=torch.float32).to(self.router.device)
        adj_tensor = adj.to(self.router.device) if adj is not None else None
        
        with torch.no_grad():
            ratios, _ = self.router.agent(state_tensor, adj_tensor)
            ratios_list = ratios.cpu().numpy().tolist()

        # 3. DISTRIBUCIÓN DE PAQUETES (Multipath)
        # Asignar fragmentos a rutas basado en el ratio (Weighted Round Robin simplificado)
        assignments = []
        total_frags = len(fragments)
        
        # Calcular cuántos paquetes van por cada ruta
        counts = [int(r * total_frags) for r in ratios_list]
        # Ajustar por errores de redondeo asignando el resto a la mejor ruta
        while sum(counts) < total_frags:
            counts[counts.index(max(counts))] += 1

        frag_idx = 0
        packets_in_flight = []

        # Estructura para el frontend: Definir rutas activas
        active_routes_info = []
        
        for route_idx, count in enumerate(counts):
            route = candidates[route_idx]
            route_fragments = fragments[frag_idx : frag_idx + count]
            frag_idx += count
            
            if not route_fragments: continue

            # Guardar info de ruta para frontend
            active_routes_info.append({
                "route_id": route_idx,
                "path": route['enlaces'], # Lista ["S0_0-S0_1", ...]
                "strategy": route['estrategia'],
                "assigned_packets": len(route_fragments),
                "ratio": ratios_list[route_idx],
                "color": ["#00ff00", "#0000ff", "#ff0000"][route_idx % 3] # Hex colors para Three.js
            })

            # Iniciar procesos de simulación para este grupo de fragmentos
            for pkt_id, frag in enumerate(route_fragments):
                p = self.env.process(
                    self.simulate_packet_travel(
                        pkt_id, frag, route, route_idx, len(route_fragments)
                    )
                )
                packets_in_flight.append(p)

        # Esperar a que todos los paquetes lleguen
        yield simpy.AllOf(self.env, packets_in_flight)
        
        print("[*] Transmisión completada.")
        
        # 4. PREPARAR RESPUESTA PARA LA API / FRONTEND
        response_payload = {
            "meta": {
                "original_size": original_size,
                "compressed_size": len(compressed),
                "processing_time_ms": proc_time,
                "total_fragments": total_frags
            },
            "routes": active_routes_info,
            "timeline": self.transmission_log # Lista cronológica de eventos para animación
        }
        
        return response_payload

    def simulate_packet_travel(self, pkt_id, data, route, route_idx, total_in_group):
        """
        Simula el paso del paquete nodo por nodo para generar eventos de animación.
        """
        path_links = route['enlaces']
        
        # Calcular latencia total de la ruta (simplificado, idealmente es hop-by-hop)
        # Usamos los datos pre-calculados del router para velocidad

        total_delay = route['delay'] 
        hop_delay = total_delay / len(path_links)
        throughput = route['throughput'] # Mbps
        if throughput == 0:
            throughput = 0.00001
        
        # Tiempo de serialización (tamaño / ancho de banda)
        packet_size_bits = len(data) * 8
        serialization_time = packet_size_bits / (throughput * 1e6)
        
        current_time = self.env.now
        
        # FRONTEND: Evento de Salida
        self.transmission_log.append({
            "time": current_time,
            "type": "PACKET_START",
            "route_idx": route_idx,
            "packet_id": pkt_id,
            "location": path_links[0].split('-')[0] # Nodo origen (ej S0_0)
        })

        # Simular viaje hop-by-hop
        for i, link in enumerate(path_links):
            u, v = link.split('-')
            
            # Simular tiempo de viaje en este enlace
            yield self.env.timeout(hop_delay + serialization_time)
            
            # FRONTEND: Evento de llegada a un nodo intermedio (Hop)
            self.transmission_log.append({
                "time": self.env.now,
                "type": "PACKET_HOP",
                "route_idx": route_idx,
                "packet_id": pkt_id,
                "location": v # Nodo actual
            })

# --- BLOQUE DE EJECUCIÓN  ---
if __name__ == "__main__":
   
    env = simpy.Environment()
    constellation = ConstellationManager(env)
    
    # Cargar Router (Modo Inferencia)
    router = IntelligentRouter(constellation, train_mode=False)
    
    
    transmitter = TransmissionSimulator(env, constellation, router)
    
    # Datos Dummy para probar
    dummy_data = "DATOS_DE_TELEMETRIA_SATELLITE," * 500 # Un string largo
    
    # Definir Origen y Destino
    src_p, src_s = 0, 0
    dst_p, dst_s = 2, 5
    
    # Ejecutar proceso
    process = env.process(transmitter.process_and_send(dummy_data, src_p, src_s, dst_p, dst_s))
    env.run()
    
    # Obtener resultados (simulando que esto se devuelve a una API Flask/FastAPI)
    result_json = process.value
    
    # Guardar un JSON para que veas qué estructura mandar al frontend
    with open("frontend_demo_data.json", "w") as f:
        json.dump(result_json, f, indent=4)
        print("\n[V] Datos exportados a frontend_demo_data.json para React")