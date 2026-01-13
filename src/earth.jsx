import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";


// Escena y cámara
// scene: contenedor de todos los objetos 3D.
// camera: define punto de vista (FOV, relación de aspecto, planos de recorte).

export default function Earth(){
const groupRef = useRef();

  // Cargar texturas
  const colorMap = new THREE.TextureLoader().load("/04_rainbow1k.jpg");
  const alphaMap = new THREE.TextureLoader().load("/02_earthspec1k.jpg");

  // Geometría y materiales
  const geo = new THREE.IcosahedronGeometry(1, 10);
  const wireMat = new THREE.MeshBasicMaterial({ color: "#aeabab", wireframe: true, opacity: 0.8, transparent: true });

  // Shader material para puntos
  const detail = 60;
  const pointsGeo = new THREE.IcosahedronGeometry(1, detail);

  const uniforms = {
    size: { value: 4.0 },
    colorTexture: { value: colorMap },
    alphaTexture: { value: alphaMap }
  };

  const vertexShader = `
    uniform float size;
    varying vec2 vUv;
    varying float vVisible;
    void main() {
      vUv = uv;
      vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
      vec3 vNormal = normalMatrix * normal;
      vVisible = step(0.0, dot( -normalize(mvPosition.xyz), normalize(vNormal)));
      gl_PointSize = size;
      gl_Position = projectionMatrix * mvPosition;
    }
  `;
  const fragmentShader = `
    uniform sampler2D colorTexture;
    uniform sampler2D alphaTexture;
    varying vec2 vUv;
    varying float vVisible;
    void main() {
      if (floor(vVisible + 0.1) == 0.0) discard;
      float alpha = 1.0 - texture2D(alphaTexture, vUv).r;
      vec3 color = texture2D(colorTexture, vUv).rgb;
      gl_FragColor = vec4(color, alpha);
    }
  `;

  const pointsMat = new THREE.ShaderMaterial({
    uniforms,
    vertexShader,
    fragmentShader,
    transparent: true
  });

  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.002;
    }
  });

  return (
    <group ref={groupRef}>
      <mesh geometry={geo} material={wireMat} />
      <points geometry={pointsGeo} material={pointsMat} />
    </group>
  );

}