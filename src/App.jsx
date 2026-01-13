// src/App.jsx
import React, { useState, Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei';
import Galaxy from './Galaxy'
import Earth from './earth.jsx'
import Sattellites from './Satellites.jsx'; 
import './App.css'

function App() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [simulationData, setSimulationData] = useState(null); // Aquí guardaremos el JSON del backend
  const [stats, setStats] = useState(null);

  // Manejar selección de archivo
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Manejar botón de Upload
  const handleUpload = async () => {
    if (!file) return alert("Por favor selecciona un archivo primero");

    setIsLoading(true);
    setSimulationData(null); // Limpiar visualización anterior
    
    const formData = new FormData();
    formData.append("file", file); // El nombre "file" debe coincidir con tu backend FastAPI

    try {
      // Asegúrate de que esta URL apunte a tu servidor Python
      const response = await fetch("http://localhost:8000/api/transmit", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Error en la transmisión con el backend");

      const data = await response.json();
      console.log("Datos recibidos del backend:", data);
      
      // Guardar datos de la simulacion
      setSimulationData(data);
      setStats(data.meta); // metadatos para mostrar

    } catch (error) {
      console.error("Error:", error);
      alert("Falló la simulación. Revisa la consola.");
    } finally {
      setIsLoading(false);
    }
  };


  return (
    
    <div className="main-container">
      <Galaxy/>
      <div className="ui-overlay">
        <h1>Transmisión Satelital DRL</h1>
        
        <div className="upload-controls">
          <input 
            type="file" 
            onChange={handleFileChange} 
            disabled={isLoading}
            className="file-input"
          />
          <button 
            onClick={handleUpload} 
            disabled={isLoading || !file}
            className="upload-btn"
          >
            {isLoading ? "Procesando y Simulando..." : "Transmitir Archivo"}
          </button>
        </div>

        {/* Panel de estadísticas si hay resultados */}
        {stats && (
          <div className="stats-panel">
            <h3>Resultados de Transmisión:</h3>
            <p>Archivo: {stats.filename}</p>
            <p>Tamaño Original: {(stats.original_size / 1024).toFixed(2)} KB</p>
            <p>Tamaño Comprimido: {(stats.compressed_size / 1024).toFixed(2)} KB</p>
            <p>Fragmentos: {stats.total_fragments}</p>
            <p>Tiempo Proc. (C++): {stats.processing_time_ms.toFixed(2)} ms</p>
          </div>
        )}
      </div>

      
      {/* --- ESCENA 3D (CANVAS) --- */}
      <Canvas camera={{ position: [0, 0, 3.5] }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1.5} />
        <Suspense fallback={null}>
          
          <Earth />
          {/* Si tenemos datos de simulación, renderizamos la visualización */}
          {simulationData && <Sattellites data={simulationData} />}
        </Suspense>
        <OrbitControls minDistance={2} maxDistance={20} enablePan={false}/>
      </Canvas>
    </div>
  )
}

export default App