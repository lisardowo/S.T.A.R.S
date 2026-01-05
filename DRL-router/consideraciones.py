import math
import torch
import numpy as np

# Constante: Velocidad de la luz (vacío)
C = 299792458 
def getNetworkState(rutasIA):
    return 


def PathDelay(q_delays: list, r_delays: list, distances: list) -> float:
    """
   
    """
    total_delay = 0
    for q, r, dist in zip(q_delays, r_delays, distances):
        # El retraso de propagación es distancia / velocidad de la luz
        propagation = dist / C
        total_delay += (q + r + propagation)
    return total_delay

def TrafficRatioConstraint(ratios: list) -> bool:
   
    
    return math.isclose(sum(ratios), 1.0)

def LinkTraffic(flows_bandwidth: list, ratios: list, packet_loss_rates: list) -> float:
    
    traffic = 0
    for b_m, w_ml, delta in zip(flows_bandwidth, ratios, packet_loss_rates):
        traffic += b_m * w_ml * delta
    return traffic

def PathThroughput(link_traffics: list) -> float:
    
    if not link_traffics: return 0.0
    return max(link_traffics)

def TrainingFunction(avg_throughput: float, avg_delay: float, beta1: float = 0.5) -> float:
    
    beta2 = 1 - beta1
    # Se añaden epsilons pequeños para evitar log(0)
    epsilon = 1e-9
    term1 = beta1 * math.log(avg_throughput + epsilon)
    term2 = beta2 * math.log(avg_delay + epsilon)
    return term1 - term2

