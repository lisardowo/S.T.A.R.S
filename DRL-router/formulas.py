import math

def mathematicalRounding(x: float) -> int:
    
    # Rounding function used to normalize the hops in the interplane - sgn(x) * floor(|x| + 1/2)
    return int(math.copysign(1, x) * math.floor(abs(x) + 0.5))

def RANN_Diference(source:float , destination:float) -> float:
    #RAAN - Right Ascension of Ascending Node
    '''
    Number of interplane hops depends on RAAN difference (RAAN_delta) of the obtis where source annd destination nodes are locatede
    Given a source - destination pair (source(Y2), destination(Y1)) difference shall be calculated as:
    '''
    
    return abs((source - destination) % (2 * math.pi))

def eastANDwest_Hops(RANN_Delta: float, Omega_Delta: float) -> dict:
    """
    Determines the cuantity of hops neded to reach destination taking both weast and east direction
    """
    Hops_west = mathematicalRounding((2 * math.pi - RANN_Delta) / Omega_Delta) # Eq 12
    Hops_east = mathematicalRounding(RANN_Delta / Omega_Delta) # Eq 13
    
    return {'west': Hops_west, 'east': Hops_east}

def phaseAngleNormalization(Destinylatitude: float, OriginLatitude: float, Hops_east: int, Hops_west: int, phase_delta: float) -> tuple:
    
    #Normalization of the phase angle difference removing the effect of satelite movement during inter-plane hops.
    
    eastLatitude_delta = (Destinylatitude - OriginLatitude - Hops_east * phase_delta) % (2 * math.pi) # Eq 15
    westLatitude_delta = (Destinylatitude - OriginLatitude + Hops_west * phase_delta) % (2 * math.pi) # Eq 16
    return eastLatitude_delta, westLatitude_delta

def FourDirectionsHops(eastLatitude_delta: float, westLatitude_delta: float, Phi_delta: float) -> dict: #TODO cambiar nombre 
    """
    Computes the hops for each cardinal direction
    round the hops to normalize the hops
    """
   
    hops: dict[str, float] = {}
    hops['north_west'] = abs(westLatitude_delta / Phi_delta)      # Eq 17
    hops['north_east'] = abs(eastLatitude_delta / Phi_delta)      # Eq 18
    hops['south_west'] = abs((2*math.pi - westLatitude_delta) / Phi_delta) # Eq 19
    hops['south_east'] = abs((2*math.pi - eastLatitude_delta) / Phi_delta) # Eq 20
    
    
    return {k: mathematicalRounding(v) for k, v in hops.items()}

def minimunHopCount(Horizontal_hops: dict, Vertical_hops: dict) -> int:
    """
    Calculate the total hops neded combining horizontal and vertical hops 
    """
    
    options = [
        Horizontal_hops['west'] + Vertical_hops['north_west'],
        Horizontal_hops['west'] + Vertical_hops['south_west'],
        Horizontal_hops['east'] + Vertical_hops['north_east'],
        Horizontal_hops['east'] + Vertical_hops['south_east']
        
    ]
    return min(options)
    
    #TODO Corregir typos, unificar nombres
    #TODO agregar funciones -> phase_delta, phi_delta, omega_delta (el progama no funcionara sin tales)
    #TODO probar todo el modulo con test cases