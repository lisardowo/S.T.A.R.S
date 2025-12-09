import * as THREE from "three";
const disclaimer = "Esta es la version web publicada mediante onrender, dado a limitaciones tecnicas, \
la comunicacion podria fallar con la API si ha pasado mucho tiempo desde su ultimo uso dando una apariencia del codigo no funcionando\
Yakucode recomienda ampliamente correr la version instalada(personal) para asegurar la funcionalidad del sistema\
las instrucciones las puede encontrar en el readme del repositorio original"
alert(disclaimer);
// Crear la escena
const scene = new THREE.Scene();

// Crear la cámara (perspectiva)
const camera = new THREE.PerspectiveCamera(
  75, // Campo de visión (FOV)
  window.innerWidth / window.innerHeight, // Relación de aspecto
  0.1, // Plano cercano
  1000 // Plano lejano
);

// Crear el renderizador y establecer su tamaño
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
const container = document.getElementById("sphere-container");
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(container.clientWidth, container.clientHeight); // match container
renderer.setClearColor(0x000000, 0); // transparent background so Galaxy shows through
container.appendChild(renderer.domElement);

// Crear la geometría del cubo
const geometry = new THREE.SphereGeometry(15, 32 , 16 );

// Crear el material del cubo (color básico)
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00,
  wireframe: true,
 });

// Crear el cubo combinando geometría y material
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere); // Agregar el cubo a la escena

// Posicionar la cámara para que vea el cubo
camera.position.z = 50;

// Función de animación para renderizar la escena
function animate() {
  requestAnimationFrame(animate); // Llamar a la función en cada frame

  // Rotar el cubo en cada frame
  sphere.rotation.x += 0.01;
  sphere.rotation.y += 0.01;
  sphere.rotation.z += 0.01;
  

  renderer.render(scene, camera); // Renderizar la escena desde la perspectiva de la cámara
}

animate(); // Iniciar la animación

// Resize handling to keep canvas/fullscreen in sync
window.addEventListener('resize', () => {
  if (!container) return;
  const w = container.clientWidth;
  const h = container.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
});

