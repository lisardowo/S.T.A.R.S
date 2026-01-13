
import React, { useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { getSatellitePosition, parseNodeId } from './utils';

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


    // PROCESAR RUTAS 
    const staticElements = useMemo(() => {
        const elements = [];
        const processedSatellites = new Set(); // no dibujar el mismo satelite

        routes.forEach((route, idx) => {
            const routeColor = new THREE.Color(route.color);
            const linePoints = [];

            // Extraer nodos únicos de los enlaces de la ruta
            route.path.forEach(linkStr => {
                const [u, v] = linkStr.split('-');
                [u, v].forEach(nodeId => {
                    if (!processedSatellites.has(nodeId)) {
                        processedSatellites.add(nodeId);
                        const coords = parseNodeId(nodeId);
                        const pos = getSatellitePosition(coords.plane, coords.sat);
                        
                        // Añadir satélite (esfera estática)
                        elements.push(
                            <mesh key={`sat-${nodeId}`} position={pos}>
                                <sphereGeometry args={[0.01, 16, 16]} />
                                <meshStandardMaterial color="#aaaaaa" emissive="#444444" />
                            </mesh>
                        );
                    }
                });
                 // Construir puntos para la línea
                 const uCoords = parseNodeId(u);
                 const vCoords = parseNodeId(v);
                 linePoints.push(getSatellitePosition(uCoords.plane, uCoords.sat));
                 linePoints.push(getSatellitePosition(vCoords.plane, vCoords.sat));
            });

            // Añadir línea de la ruta
            if (linePoints.length > 0) {
                 // Usamos una línea simple de Three.js. 
                 // Para líneas gruesas se necesitaría 'three-stdlib' Line2, pero esto es más simple.
                 const lineGeometry = new THREE.BufferGeometry().setFromPoints(linePoints);
                 elements.push(
                    <line key={`route-line-${idx}`}>
                        <primitive object={lineGeometry} />
                        <lineBasicMaterial color={routeColor} linewidth={2} opacity={0.6} transparent />
                    </line>
                 );
            }
        });
        return elements;
    }, [routes]);


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