
import React, { useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { getSatellitePosition, parseNodeId, PLANES, SATS_PER_PLANE } from './utils';
// Componente para un solo paquete animado
const Packet = ({ routeData, timeline, simulationTime }) => {
    const meshRef = useRef();
    const routeColor = new THREE.Color(routeData.color);

    useFrame(() => {
        if (!meshRef.current) return;

        // Encontrar en qué segmento del viaje debería estar el paquete basado en el tiempo actual
        let startNodeId = null;
        let endNodeId = null;
        let progress = 0;

        // Iteramos el timeline para encontrar el hop actual
        for (let i = 0; i < timeline.length - 1; i++) {
            const currentEvent = timeline[i];
            const nextEvent = timeline[i+1];

            // Si el tiempo actual de simulación está entre dos eventos
            if (simulationTime >= currentEvent.time && simulationTime < nextEvent.time) {
                startNodeId = currentEvent.location;
                // El siguiente evento nos dice a dónde vamos
                // (Asumimos que un evento HOP indica la llegada al nodo)
                endNodeId = nextEvent.location; 

                // Calcular progreso entre estos dos nodos (0.0 a 1.0)
                const timeDiff = nextEvent.time - currentEvent.time;
                progress = (simulationTime - currentEvent.time) / timeDiff;
                break;
            }
        }

        if (startNodeId && endNodeId) {
            // Obtener posiciones 3D
            const startCoords = parseNodeId(startNodeId);
            const endCoords = parseNodeId(endNodeId);
            const startPos = getSatellitePosition(startCoords.plane, startCoords.sat);
            const endPos = getSatellitePosition(endCoords.plane, endCoords.sat);

            // Interpolar posición (Lerp) y actualizar el mesh
            meshRef.current.position.lerpVectors(startPos, endPos, progress);
            meshRef.current.visible = true;
        } else {
            // Si ya terminó el viaje o no ha empezado
            meshRef.current.visible = false;
        }
    });

    return (
        <mesh ref={meshRef}>
            {/* El paquete es una esfera un poco más grande que los satélites */}
            <sphereGeometry args={[0.015, 8, 8]} />
            <meshBasicMaterial color={routeColor.clone().multiplyScalar(2)} /> {/* Color brillante */}
        </mesh>
    );
};


const Satellites = ({ data }) => {
    // data es el JSON completo recibido del backend
    const { routes, timeline } = data;
    
    // Estado para controlar el tiempo de la animación
    const [simulationTime, setSimulationTime] = useState(0);
    

    // Encontrar el tiempo máximo para saber cuándo reiniciar/parar
    const maxTime = useMemo(() => {
        if (timeline.length === 0) return 0;
        return timeline[timeline.length - 1].time;
    }, [timeline]);

    // Hook principal de animación (loop)
    useFrame((state, delta) => {
        if (maxTime === 0) return;

    
        setSimulationTime(prev => {
            const nextTime = prev + (delta * 500); // Ajustar velocidad
            if (nextTime > maxTime + 100) return 0; // Reiniciar ciclo
            return nextTime;
        });
    });


   

    // 2. Calcular el set de satélites usados en las rutas
    const usedSatellites = useMemo(() => {
        const set = new Set();
        routes.forEach(route => {
            route.path.forEach(linkStr => {
                const [u, v] = linkStr.split('-');
                set.add(u);
                set.add(v);
            });
        });
        return set;
    }, [routes]);

    // 3. Renderizar todos los satélites, destacando los usados y mostrando la malla completa
    const staticElements = useMemo(() => {
        const elements = [];
        
        // Renderizar todos los satélites
        for (let plane = 0; plane < PLANES; plane++) {
            for (let sat = 0; sat < SATS_PER_PLANE; sat++) {
                const nodeId = `S${plane}_${sat}`;
                const pos = getSatellitePosition(plane, sat);
                const isUsed = usedSatellites.has(nodeId);
                
                elements.push(
                    <mesh key={`sat-${nodeId}`} position={pos}>
                        <sphereGeometry args={[isUsed ? 0.015 : 0.008, 16, 16]} />
                        <meshStandardMaterial 
                            color={isUsed ? "#FFFF00" : "#666666"}
                            emissive={isUsed ? "#FFFF00" : "#333333"}
                            emissiveIntensity={isUsed ? 2.0 : 0.3}
                        />
                    </mesh>
                );
            }
        }

        // Conexiones intra-plano (dentro de cada plano orbital)
        for (let plane = 0; plane < PLANES; plane++) {
            for (let sat = 0; sat < SATS_PER_PLANE; sat++) {
                const nextSat = (sat + 1) % SATS_PER_PLANE;
                const pos1 = getSatellitePosition(plane, sat);
                const pos2 = getSatellitePosition(plane, nextSat);
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([pos1, pos2]);
                elements.push(
                    <line key={`intra-${plane}-${sat}`}>
                        <primitive object={lineGeometry} />
                        <lineBasicMaterial color="#4a4a4a" opacity={0.2} transparent />
                    </line>
                );
            }
        }

        // Conexiones inter-plano (entre planos adyacentes)
        for (let plane = 0; plane < PLANES; plane++) {
            const nextPlane = (plane + 1) % PLANES;
            for (let sat = 0; sat < SATS_PER_PLANE; sat++) {
                const pos1 = getSatellitePosition(plane, sat);
                const pos2 = getSatellitePosition(nextPlane, sat);
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([pos1, pos2]);
                elements.push(
                    <line key={`inter-${plane}-${sat}`}>
                        <primitive object={lineGeometry} />
                        <lineBasicMaterial color="#3a3a3a" opacity={0.15} transparent />
                    </line>
                );
            }
        }

        // Añadir las líneas de las rutas (cada una con su color)
        routes.forEach((route, idx) => {
            const routeColor = route.color; // Usar directamente el string hex
            route.path.forEach(linkStr => {
                const [u, v] = linkStr.split('-');
                const uCoords = parseNodeId(u);
                const vCoords = parseNodeId(v);
                const pos1 = getSatellitePosition(uCoords.plane, uCoords.sat);
                const pos2 = getSatellitePosition(vCoords.plane, vCoords.sat);
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([pos1, pos2]);
                elements.push(
                    <line key={`route-${idx}-${linkStr}`}>
                        <primitive object={lineGeometry} />
                        <lineBasicMaterial color={routeColor} linewidth={3} opacity={0.8} transparent />
                    </line>
                );
            });
        });
        
        return elements;
    }, [routes, usedSatellites]);


    // 2. PROCESAR PAQUETES ANIMADOS
    // Filtramos el timeline para obtener IDs de paquete únicos por ruta
    const packetElements = useMemo(() => {
        const packetsToRender = [];
        
        routes.forEach((route, routeIdx) => {
            // Encontrar cuántos paquetes únicos hay en esta ruta mirando el timeline
            const uniquePacketIds = new Set(
                timeline
                .filter(event => event.route_idx === routeIdx)
                .map(event => event.packet_id)
            );
            
            uniquePacketIds.forEach(pktId => {
                // Filtrar solo los eventos de este paquete específico
                const packetTimeline = timeline.filter(
                    e => e.route_idx === routeIdx && e.packet_id === pktId
                ).sort((a,b) => a.time - b.time);

                 packetsToRender.push(
                    <Packet 
                        key={`pkt-${routeIdx}-${pktId}`}
                        routeData={route}
                        timeline={packetTimeline}
                        simulationTime={simulationTime}
                    />
                );
            });
        });
        return packetsToRender;
    }, [routes, timeline, simulationTime]);


    return (
        <group>
            {staticElements}
            {packetElements}
        </group>
    );
};

export default Satellites;