import math

def mathematicalRounding(x: float) -> int:
    
    # Rounding function used to normalize the hops in the interplane - sgn(x) * floor(|x| + 1/2)
    return int(math.copysign(1, x) * math.floor(abs(x) + 0.5))

def RAAN_Delta(source:float , destination:float) -> float:
    #RAAN - Right Ascension of Ascending Node
    '''
    Number of interplane hops depends on RAAN difference (RAAN_delta) of the obtis where source annd destination nodes are locatede
    Given a source - destination pair (source(Y2), destination(Y1)) difference shall be calculated as:
    '''
    
    return abs((destination - source) % (2 * math.pi))

def phaseDelta( NumberOfSatelites: int, NumberOfPlanes: int, phase: int) -> float:
    """
    Phase angle difference between adjacent planes
    """
    totalSatelites = NumberOfPlanes * NumberOfSatelites
      # Eq 8
    return (((2 * math.pi) * phase) / totalSatelites)  # Eq 9

def eastANDwest_Hops(RAAN_Delta: float, NumberOfPlanes: int) -> dict:
    """
    Determines the cuantity of hops neded to reach destination taking both west and east direction
    """
    Omega_Delta = (2 * math.pi) / NumberOfPlanes  # Eq 11
    Hops_west = mathematicalRounding((2 * math.pi - RAAN_Delta) / Omega_Delta) # Eq 12
    Hops_east = mathematicalRounding(RAAN_Delta / Omega_Delta) # Eq 13
    
    return {'west': Hops_west, 'east': Hops_east}

def phaseAngleNormalization(Destinylatitude: float, OriginLatitude: float, Hops_east: int, Hops_west: int, phase_delta: float) -> tuple:
    
    #Normalization of the phase angle difference removing the effect of satelite movement during inter-plane hops.
    
    eastLatitude_delta = (Destinylatitude - OriginLatitude - Hops_east * phase_delta) % (2 * math.pi) # Eq 15
    westLatitude_delta = (Destinylatitude - OriginLatitude + Hops_west * phase_delta) % (2 * math.pi) # Eq 16
    return eastLatitude_delta, westLatitude_delta



def CardinalDirectionsHops(eastLatitude_delta: float, westLatitude_delta: float, NumberOfSatelites: float) -> dict: 
    """
    Computes the hops for each cardinal direction
    round the hops to normalize the hops
    """
    Phi_delta = (2 * math.pi) / NumberOfSatelites
    hops: dict[str, float] = {}
    hops['north_west'] = abs(westLatitude_delta / Phi_delta)      # Eq 17
    hops['north_east'] = abs(eastLatitude_delta / Phi_delta)      # Eq 18
    hops['south_west'] = abs((2*math.pi - westLatitude_delta) / Phi_delta) # Eq 19
    hops['south_east'] = abs((2*math.pi - eastLatitude_delta) / Phi_delta) # Eq 20
    
    
    return {k: mathematicalRounding(v) for k, v in hops.items()}

def GenerateConections(SourcePlane, SourceSatelite, DestinyPlane, DestinySatelite, strategy, NumberPlanes, NumberSatelites) -> list[str]:
   
    enlaces = []
    CurrentPlane, CurrentSatelite = SourcePlane, SourceSatelite
    
    # Determinamos el paso basándonos en la estrategia de la ruta
    StepPlane = 1 if "E" in strategy else -1
    StepSatelite = 1 if "N" in strategy else -1

    # Movimiento Horizontal (Inter-plano)
    while CurrentPlane != DestinyPlane:
        NextPlane = (CurrentPlane + StepPlane) % NumberPlanes
        enlaces.append(f"S-{CurrentPlane}_{CurrentSatelite}-S{NextPlane}_{CurrentSatelite}")
        CurrentPlane = NextPlane
        
    # Movimiento Vertical (Intra-plano)
    while CurrentSatelite != DestinySatelite:
        NextSatelite = (CurrentSatelite + StepSatelite) % NumberSatelites
        enlaces.append(f"S{CurrentPlane}_{CurrentSatelite}-S{CurrentPlane}_{NextSatelite}")
        CurrentSatelite = NextSatelite
    
    
    return enlaces



def GetOptimalPaths(sourceSatelite, sourcePlane, destinationSatelite, destinationPlane , Horizontal_hops: dict, Vertical_hops: dict, SubOptimalPaths: int, NumberSatelites, NumberPlanes) -> list: #TODO Modificar SubOptimalPaths para que sea obtenido dinacmicamente
   
    raw_options = [
        {"estrategia": "NW", "hops": Horizontal_hops['west'] + Vertical_hops['north_west']},
        {"estrategia": "SW", "hops": Horizontal_hops['west'] + Vertical_hops['south_west']},
        {"estrategia": "NE", "hops": Horizontal_hops['east'] + Vertical_hops['north_east']},
        {"estrategia": "SE", "hops": Horizontal_hops['east'] + Vertical_hops['south_east']}
    ]

   
    sorted_paths = sorted(raw_options, key=lambda x: x['hops'])

    rutas_candidatas = []
    
    
    for i in range(min(SubOptimalPaths, len(sorted_paths))):
        path_data = sorted_paths[i]

        conecctions = GenerateConections(sourceSatelite, sourcePlane, destinationSatelite, destinationPlane, path_data['estrategia'], NumberSatelites, NumberPlanes)
        
        rutas_candidatas.append({
            "id": i + 1,
            "estrategia": path_data['estrategia'],
            "hops": path_data['hops'],
            "enlaces": conecctions
        })

    return rutas_candidatas

GenerateConections(0, 0, 2, 2, "NW", 4, 4)