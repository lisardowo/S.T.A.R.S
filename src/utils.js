
import * as THREE from 'three';



const disclaimer = "you are using the web version (published by onrender), due to technical limitations, \
comunication with the API could not properly work if its been time since the last time it was used. This may give the appeareance of the code not working\
Yakucode explicitly suggest run the installed version(personal) in order to assure the stability of the system\
instructions will be found in the readme of the original repository"
alert(disclaimer);

// ----- ELIMINAR EL COMENTARIO ARRIBA PARA LA PUBLICACION FINAL ------



//variables de configuracion
//TODO modificar las variables para que sean procedurales
const TOTAL_PLANES = 3; 
const SATS_PER_PLANE = 22; 
const EARTH_RADIUS = 1; 
const ORBIT_ALTITUDE = 0.3; //Altitud a la que orbitan los satelites
const ORBIT_RADIUS = EARTH_RADIUS + ORBIT_ALTITUDE;

//Funcion para convertir la id (plano, índice) a posiciones xyz
 
export function getSatellitePosition(planeIdx, satIdx) {
    // 1. Calcular ángulos esféricos (Phi y Theta)
    // Espaciamos los planos equitativamente alrededor del ecuador (Theta)
    const theta = (planeIdx / TOTAL_PLANES) * Math.PI * 2;

    // Espaciamos los satélites dentro del plano a lo largo de la órbita (Phi)
    // Añadimos un pequeño desfase (phase shift) entre planos para que no parezca una cuadrícula
    const phaseShift = (planeIdx % 2 === 0) ? 0 : (Math.PI / SATS_PER_PLANE);
    const phi = (satIdx / SATS_PER_PLANE) * Math.PI * 2 + phaseShift;

    // 2. Convertir coordenadas esféricas a cartesianas (X, Y, Z)
    // Usamos una fórmula estándar para envolver una esfera
    const x = ORBIT_RADIUS * Math.sin(phi) * Math.cos(theta);
    const y = ORBIT_RADIUS * Math.cos(phi); // Eje Y es "arriba" en Three.js por defecto
    const z = ORBIT_RADIUS * Math.sin(phi) * Math.sin(theta);

    return new THREE.Vector3(x, y, z);
}


//Funcion para convertir los nodos del backend
// (ej. "S0_5" -> plano 0, sat 5)
 
export function parseNodeId(nodeStr) {
    //  formato "S{plane}_{sat}" ej: S0_5
    const parts = nodeStr.substring(1).split('_');
    return {
        plane: parseInt(parts[0]),
        sat: parseInt(parts[1])
    };
}