import simpy
import random

# --- CONSTANTES HARCODEDAS (Como solicitado) ---
NUMBER_OF_PLANES = 24   # N_P
NUMBER_OF_SATS = 66    # N_S
# -----------------------------------------------

class Satellite:
    def __init__(self, env, plane_id, sat_id):
        self.env = env
        self.plane_id = plane_id
        self.sat_id = sat_id
        
        # Identificador único para logs
        self.full_id = f"S{plane_id}_{sat_id}"
        
        # Propiedades dinámicas (Simuladas)
        # Capacidad máxima de procesamiento (packets/sec)
        self.max_processing_power = random.uniform(800, 1200) 
        # Ancho de banda máximo del enlace (Mbps)
        self.max_bandwidth = 1000.0 
        
        # Estado actual (Variable en el tiempo)
        self.current_load = random.uniform(0.1, 0.4) # 10% a 40% de carga inicial
        self.available_bandwidth = self.max_bandwidth
        
        # Iniciar proceso de comportamiento
        self.action = env.process(self.run())

    def run(self):
        """Ciclo de vida del satélite en SimPy"""
        while True:
            # Simular paso del tiempo y cambio de condiciones
            # Cada 1 a 5 segundos de simulación, la carga cambia
            yield self.env.timeout(random.randint(1, 5))
            
            # Fluctuación procedural de la carga (Simula tráfico de usuarios)
            change = random.uniform(-0.1, 0.1)
            self.current_load = max(0.0, min(1.0, self.current_load + change))
            
            # El ancho de banda disponible fluctúa inversamente a la carga
            self.available_bandwidth = self.max_bandwidth * (1 - (self.current_load * 0.5))

    def get_state(self):
        """Retorna el estado actual para la IA"""
        return {
            'id': self.full_id,
            'plane': self.plane_id,
            'sat': self.sat_id,
            'load': self.current_load, # Afecta q_delay
            'bw': self.available_bandwidth # Afecta throughput
        }

class ConstellationManager:
    def __init__(self, env):
        self.env = env
        self.satellites = {} # Diccionario mapeado por "S{plane}_{sat}"
        self.planes = NUMBER_OF_PLANES
        self.sats_per_plane = NUMBER_OF_SATS
        
        self._generate_constellation()

    def _generate_constellation(self):
        """Generación procedural de la constelación"""
        print(f"[*] Generando constelación procedural: {self.planes} Planos, {self.sats_per_plane} Sats/Plano")
        for p in range(self.planes):
            for s in range(self.sats_per_plane):
                # Crear satélite y añadir a la gestión
                sat = Satellite(self.env, p, s)
                self.satellites[sat.full_id] = sat

    def get_satellite(self, plane_idx, sat_idx):
        key = f"S{plane_idx}_{sat_idx}"
        return self.satellites.get(key)

    def get_link_metrics(self, u, v, packet_size=1500):
        """
        Calcula métricas en tiempo real entre dos nodos.
        Integra lógica de 'consideraciones.py' simulada.
        """
        node_u = self.satellites[u]
        node_v = self.satellites[v]

        u_active = getattr(node_u, "is_active", getattr(node_u, "active", True))
        v_active = getattr(node_v, "is_active", getattr(node_v, "active", True))
        v_bw = float(getattr(node_v, "available_bandwidth", 0.0))

        if not u_active or not v_active or v_bw <= 0.0:
            return {
                'q_delay': 1e6,
                'r_delay': 1e6,
                'distance': float('inf'),
                'link_throughput': node_v.available_bandwidth,
                'link_down': True,
            }

        denom = max(v_bw * 1e6, 1e-9)
        r_delay = packet_size / denom

        # Distancia aproximada (simplificada para simulación, idealmente usaría física orbital)
        # Aquí usamos una distancia base + ruido procedural
        base_dist = 500000 # metros (intra-plane)
        if node_u.plane_id != node_v.plane_id:
            base_dist = 800000 # metros (inter-plane)
            
        distance = base_dist + random.uniform(-1000, 1000)

        # Queue Delay (q) basado en la carga del nodo destino
        q_delay = node_v.current_load * 0.05 # max 50ms si está al 100%
        
        # Link Traffic actual (simulado)
        current_traffic = node_v.max_bandwidth - node_v.available_bandwidth
        
        return {
            'q_delay': q_delay,
            'r_delay': r_delay,
            'distance': distance,
            'link_throughput': node_v.available_bandwidth,
            'link_down': False,
        }
        
    def fail_satellite(self, plane_id, sat_id):
        """Desactiva un satélite para probar la resiliencia de la GNN."""
        sat_id_str = f"S{plane_id}_{sat_id}"
        if sat_id_str in self.satellites:
       
            self.satellites[sat_id_str].available_bandwidth = 0.000001
            self.satellites[sat_id_str].current_load = 1.0
            print(f"[!] FALLO : Satélite {sat_id_str} fuera de servicio.") #TODO corregir logica de sobreescritura de estado


    def recover_all_satellites(self):
        """Restaura la salud de todos los satélites de la constelación."""
        for sat in self.satellites.values():
            sat.available_bandwidth = sat.max_bandwidth
            sat.current_load = random.uniform(0.1, 0.4)
        print("[*] Constelación restaurada: Todos los sistemas operativos.")


# Bloque para probar solo este archivo
if __name__ == "__main__":
    env = simpy.Environment()
    constellation = ConstellationManager(env)
    env.run(until=10)
    print("Estado del satélite S0_0 tras 10 ticks:", constellation.get_satellite(0,0).get_state())