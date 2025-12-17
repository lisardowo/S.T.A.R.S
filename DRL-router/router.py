import time
import math
import formulas
inicio = time.time()
# --- CONFIGURACIÓN DE LA CONSTELACIÓN (Ej. Iridium) ---
# Según tabla 1 del paper [cite: 538]
N_P = 6       # Número de planos
N_S = 11      # Satélites por plano
F = 1         # Factor de fase (asumido estándar para pruebas)

# --- DEFINICIÓN DE SATÉLITES (Origen y Destino) ---
# Posiciones en radianes (Plano/RAAN, Fase/Latitud)
# Satélite A (Origen): Plano 0, Fase 0
sat_source_RAAN = 0.0
sat_source_lat = 0.0

# Satélite B (Destino): Plano 2 (aprox 2.09 rad), Fase casi opuesta (3.0 rad)
# Esto debería forzar una ruta interesante (saltar planos y moverse en órbita)
sat_dest_RAAN = (2 * math.pi / N_P) * 2  
sat_dest_lat = 3.0

print(f"--- INICIO DIAGNÓSTICO ---")
print(f"Configuración: {N_P} planos, {N_S} sats/plano, Fase F={F}")
print(f"Origen (RAAN, Lat): ({sat_source_RAAN:.2f}, {sat_source_lat:.2f})")
print(f"Destino (RAAN, Lat): ({sat_dest_RAAN:.2f}, {sat_dest_lat:.2f})")
print("-" * 30)

# 1. Calcular Delta RAAN (Corrigiendo el orden de resta aquí para la prueba)
# Nota: En tu formulas.py está (source - dest), debería ser (dest - source)
raan_diff = formulas.RAAN_Delta(sat_source_RAAN, sat_dest_RAAN)
print(f"1. Delta RAAN: {raan_diff:.4f} rad")

# 2. Calcular Delta de Fase (Delta f)
delta_f = formulas.phaseDelta(N_S, N_P, F)
print(f"2. Delta f (desfase inter-plano): {delta_f:.4f} rad")

# 3. Saltos Horizontales (Inter-plano)
h_hops = formulas.eastANDwest_Hops(raan_diff, N_P)
print(f"3. Saltos Horizontales calculados: {h_hops}")

# 4. Normalización de ángulos (Intra-plano)
# Calcula cuánto se 'desajustó' la fase al moverse horizontalmente
east_lat_delta, west_lat_delta = formulas.phaseAngleNormalization(
    sat_dest_lat, sat_source_lat, h_hops['east'], h_hops['west'], delta_f
)

# 5. Saltos Verticales (Intra-plano)
# Calcula saltos necesarios hacia arriba/abajo para corregir el desajuste
v_hops = formulas.CardinalDirectionsHops(east_lat_delta, west_lat_delta, N_S)
print(f"5. Saltos Verticales calculados: {v_hops}")

# 6. SELECCIÓN DE RUTA ÓPTIMA (Lógica mejorada para mostrar detalles)
# Reconstruimos las opciones para poder imprimir cuál ganó
opciones_detalladas = [
    {
        'camino': 'Oeste -> Noroeste (Arriba)',
        'h_dir': 'west', 'v_dir': 'north_west',
        'h_count': h_hops['west'], 'v_count': v_hops['north_west'],
        'total': h_hops['west'] + v_hops['north_west']
    },
    {
        'camino': 'Oeste -> Suroeste (Abajo)',
        'h_dir': 'west', 'v_dir': 'south_west',
        'h_count': h_hops['west'], 'v_count': v_hops['south_west'],
        'total': h_hops['west'] + v_hops['south_west']
    },
    {
        'camino': 'Este -> Noreste (Arriba)',
        'h_dir': 'east', 'v_dir': 'north_east',
        'h_count': h_hops['east'], 'v_count': v_hops['north_east'],
        'total': h_hops['east'] + v_hops['north_east']
    },
    {
        'camino': 'Este -> Sureste (Abajo)',
        'h_dir': 'east', 'v_dir': 'south_east',
        'h_count': h_hops['east'], 'v_count': v_hops['south_east'],
        'total': h_hops['east'] + v_hops['south_east']
    }
]

# Elegir el mínimo basado en 'total'
ganador = min(opciones_detalladas, key=lambda x: x['total'])

print("-" * 30)
print("--- RESULTADO FINAL ---")
print(f"Ruta más corta (Saltos Totales): {ganador['total']}")
print(f"Dirección General: {ganador['camino']}")
print("Instrucciones:")
print(f"  1. Moverse {ganador['h_count']} planos hacia {ganador['h_dir']}.")
print(f"  2. Moverse {ganador['v_count']} posiciones en órbita hacia {ganador['v_dir']}.")
print("-" * 30)

# Verificación de todas las combinaciones posibles (solicitado por usuario)
print("Resumen de todas las rutas candidatas:")
for opt in opciones_detalladas:
    estado = "[ELEGIDO]" if opt == ganador else ""
    print(f"  * {opt['camino']}: {opt['total']} saltos (H:{opt['h_count']} + V:{opt['v_count']}) {estado}")
fin = time.time()
print(f"--- FIN DIAGNÓSTICO (Tiempo total: {fin - inicio:.4f} segundos) ---")