import * as THREE from "three";


/*const disclaimer = "Esta es la version web publicada mediante onrender, dado a limitaciones tecnicas, \
la comunicacion podria fallar con la API si ha pasado mucho tiempo desde su ultimo uso dando una apariencia del codigo no funcionando\
 Yakucode recomienda ampliamente correr la version instalada(personal) para asegurar la funcionalidad del sistema\
 las instrucciones las puede encontrar en el readme del repositorio original"
alert(disclaimer);*/

// ----- ELIMINAR EL COMENTARIO ARRIBA PARA LA PUBLICACION FINAL ------

// Escena y cámara
// scene: contenedor de todos los objetos 3D.
// camera: define punto de vista (FOV, relación de aspecto, planos de recorte).
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 0, 3.5); // Puedes alejar/acercar con el eje Z (p.ej. 2.5 - 10)

// Renderizador: dibuja la escena; alpha true para fondo transparente (Galaxy visible).
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
const container = document.getElementById("sphere-container"); // Contenedor overlay en el DOM
renderer.setPixelRatio(window.devicePixelRatio); // Calidad en pantallas HiDPI
const w = container ? container.clientWidth : window.innerWidth;
const h = container ? container.clientHeight : window.innerHeight;
renderer.setSize(w, h); // tamaño del canvas
renderer.setClearColor(0x000000, 0); // color de limpieza RGBA (alpha 0 = transparente)
if (container) container.appendChild(renderer.domElement);


//scene.add(sphere); // Agregar el cubo a la escena

// Posicionar la cámara para que vea el cubo
//camera.position.set = (0,0,3.5);
camera.position.z = 5
// Texturas: mapas usados en los shaders.
// Usa rutas desde la carpeta public/ (Vite sirve /archivo.ext).
const textureLoader = new THREE.TextureLoader();
const colorMap = textureLoader.load("/04_rainbow1k.jpg"); // Colores de la superficie
const elevMap = textureLoader.load("/01_earthbump1k.jpg"); // Relieve/altura (grises)
const alphaMap = textureLoader.load("/02_earthspec1k.jpg"); // Especular/alpha

const globeGroup = new THREE.Group();

scene.add(globeGroup)
// Esfera guía en wireframe (opcional)
// Cambia subdivisión (segundo parámetro) para más/menos detalle del wireframe.
const geo = new THREE.IcosahedronGeometry(1, 10);
const mat = new THREE.MeshBasicMaterial({ color: 0x202020, wireframe: true });
const wireSphere = new THREE.Mesh(geo, mat);
globeGroup.add(wireSphere);

// Globo como nube de puntos con shaders (sin OrbitControls ni starfield).
// detail: subdivisión de la malla base (más alto = más puntos).
const detail = 120;
const pointsGeo = new THREE.IcosahedronGeometry(1, detail);

const vertexShader = `
  uniform float size;
  uniform sampler2D elevTexture;

  varying vec2 vUv;
  varying float vVisible;

  void main() {
    vUv = uv;
    vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
    float elv = texture2D(elevTexture, vUv).r;
    vec3 vNormal = normalMatrix * normal;
    vVisible = step(0.0, dot( -normalize(mvPosition.xyz), normalize(vNormal)));
    // Desplazamiento por relieve (0.35 * elv). Ajusta este factor si deseas más/menos relieve.
    mvPosition.z += 0.35 * elv;
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
const uniforms = {
  size: { value: 4.0 }, // tamaño de cada punto (sube/baja para más grande/pequeño)
  colorTexture: { value: colorMap }, // mapa de color
  elevTexture: { value: elevMap }, // mapa de relieve
  alphaTexture: { value: alphaMap } // mapa para transparencia/especular
};
const pointsMat = new THREE.ShaderMaterial({
  uniforms,
  vertexShader,
  fragmentShader,
  transparent: true // permite ver fondo (Galaxy) y blending de puntos
});
const points = new THREE.Points(pointsGeo, pointsMat);
globeGroup.add(points);

// Función de animación para renderizar la escena
function animate() {
  requestAnimationFrame(animate); // bucle de render por frame

  // Rotación del grupo para animación (ajusta velocidad)
  globeGroup.rotation.y += 0.002;

  renderer.render(scene, camera); // dibuja la escena desde la cámara
}

animate(); // Iniciar la animación

// Resize handling to keep canvas/fullscreen in sync
window.addEventListener('resize', () => {
  if (!container) return;
  const w = container.clientWidth; // ancho del contenedor
  const h = container.clientHeight; // alto del contenedor
  renderer.setSize(w, h); // redimensiona el canvas
  camera.aspect = w / h; // actualiza relación de aspecto
  camera.updateProjectionMatrix(); // aplica cambios a la proyección
});

