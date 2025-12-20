import math
import torch
import numpy as np

# Constante: Velocidad de la luz (vacío)
C = 299792458 

def PathDelay(q_delays: list, r_delays: list, distances: list) -> float:
    """
    Ecuación (1): Calcula el retraso total de una ruta (path).
    [cite: 118]
    
    Args:
        q_delays: Lista de retrasos de cola por enlace (queuing delay).
        r_delays: Lista de retrasos de procesamiento por enlace.
        distances: Lista de distancias físicas de cada enlace en la ruta.
    
    Returns:
        float: Retraso total (propagación + cola + procesamiento).
    """
    total_delay = 0
    for q, r, dist in zip(q_delays, r_delays, distances):
        # El retraso de propagación es distancia / velocidad de la luz
        propagation = dist / C
        total_delay += (q + r + propagation)
    return total_delay

def TrafficRatioConstraint(ratios: list) -> bool:
    """
    Ecuación (2): Restricción de división de tráfico.
    [cite: 120]
    La suma de los ratios de tráfico (omega) para todos los subflujos debe ser 1.
    
    Args:
        ratios: Lista de proporciones de tráfico asignadas a cada camino (w_m,l).
    
    Returns:
        bool: True si la suma es 1 (con margen de error por punto flotante).
    """
    return math.isclose(sum(ratios), 1.0)

def LinkTraffic(flows_bandwidth: list, ratios: list, packet_loss_rates: list) -> float:
    """
    Ecuación (3): Calcula el tráfico total en un enlace específico 'e_j'.
    [cite: 120]
    
    Args:
        flows_bandwidth: Demanda de ancho de banda de cada flujo 'm' (b_m).
        ratios: Ratio asignado a ese flujo en este enlace específico.
        packet_loss_rates: Tasa de pérdida de paquetes (delta).
        
    Returns:
        float: Tráfico total en el enlace.
    """
    traffic = 0
    for b_m, w_ml, delta in zip(flows_bandwidth, ratios, packet_loss_rates):
        traffic += b_m * w_ml * delta
    return traffic

def PathThroughput(link_traffics: list) -> float:
    """
    Ecuación (5): Throughput de una ruta (cuello de botella).
    [cite: 121]
    En el paper se define como el máximo tráfico de sus enlaces constituyentes,
    aunque en redes reales suele ser el mínimo de capacidad disponible (bottleneck).
    Implementado literalmente como el paper: max{f_e}.
    
    Args:
        link_traffics: Tráfico actual en cada enlace de la ruta.
    """
    if not link_traffics: return 0.0
    return max(link_traffics)

def TrainingFunction(avg_throughput: float, avg_delay: float, beta1: float = 0.5) -> float:
    """
    Ecuación (6): Función de Utilidad (Recompensa).
    [cite: 122]
    Se usa para entrenar al agente RL. Busca maximizar throughput y minimizar delay.
    
    Args:
        avg_throughput: Throughput promedio actual.
        avg_delay: Retraso promedio actual.
        beta1: Coeficiente de importancia para throughput (beta2 será 1 - beta1).
    """
    beta2 = 1 - beta1
    # Se añaden epsilons pequeños para evitar log(0)
    epsilon = 1e-9
    term1 = beta1 * math.log(avg_throughput + epsilon)
    term2 = beta2 * math.log(avg_delay + epsilon)
    return term1 - term2