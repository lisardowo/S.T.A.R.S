
import React, { useState, Suspense, useEffect } from 'react'
// Helper to generate random box-shadow for stars
function generateBoxShadow(numStars, w = 2000, h = 2000) {
  let arr = [];
  for (let i = 0; i < numStars; i++) {
    const x = Math.random() * w;
    const y = Math.random() * h;
    arr.push(`${x.toFixed(1)}px ${y.toFixed(1)}px #FFF`);
  }
  return arr.join(', ');
}

import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei';
import Earth from './earth.jsx'
import Sattellites from './Satellites.jsx'; 
import './App.css'

function App() {
    // Star layers state
    const [starShadows, setStarShadows] = useState({
      small: '',
      medium: '',
      big: ''
    });

    useEffect(() => {
      setStarShadows({
        small: generateBoxShadow(700),
        medium: generateBoxShadow(200),
        big: generateBoxShadow(100)
      });
    }, []);

  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [simulationData, setSimulationData] = useState(null); //use state to store JSON
  const [stats, setStats] = useState(null);

  // handle file upload
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };
  const handleDownload = (data, filename = "simulationResults.json") => {
    if (!data) return;
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
    const href = URL.createObjectURL(blob);
    const downloadLink = document.createElement('a');
    downloadLink.href = href;
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    URL.revokeObjectURL(href);
  };
  // Manejar botón de Upload
  const handleUpload = async () => {
    if (!file) return alert("Please upload a file first");

    setIsLoading(true);
    setSimulationData(null); // delete previous render
    
    const formData = new FormData();
    formData.append("file", file); 

    try {
      
      const response = await fetch("http://localhost:8000/api/transmit", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Error conecting to the API");

      const data = await response.json();
      console.log("Data received from backend:", data);
      
      // Save Simulation data
      setSimulationData(data);
      setStats(data.meta); // metadata to show

    } catch (error) {
      console.error("Error:", error);
      alert("Simulation has failed. Check the console .");
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="main-container">
      {/* Star layers */}
      <div id="stars" style={{ boxShadow: starShadows.small }} />
      <div id="stars2" style={{ boxShadow: starShadows.medium }} />
      <div id="stars3" style={{ boxShadow: starShadows.big }} />

      <div className="ui-overlay">
        <h1>S.T.A.R.S satelitall simulation</h1>
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
            className="generic-btn"
          >
            {isLoading ? "Processing" : "Send File"}
          </button>
        </div>
        {/* Stadistics Panel (if theres results)*/}
        {stats && (
          <div className="stats-panel">
            <h3>Transsmision Results:</h3>
            <p>File: {stats.filename}</p>
            <p>Original Size: {(stats.original_size / 1024).toFixed(2)} KB</p>
            <p>Compressed Size: {(stats.compressed_size / 1024).toFixed(2)} KB</p>
            <p>Fragments: {stats.total_fragments}</p>
            <p>Procces Time. (C++): {stats.processing_time_ms.toFixed(2)} ms</p>
            <br/>
            <button 
              onClick={() => handleDownload(simulationData, stats?.filename ? `result_${stats.filename}.json` : "simulation_result.json")}
              className='generic-btn'
            >
              Download JSON
            </button>
          </div>
        )}
      </div>

      {/* ---  3D Escene (CANVAS) --- */}
      <Canvas camera={{ position: [0, 0, 3.5] }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1.5} />
        <Suspense fallback={null}>
          <Earth />
          {/* If theres simulation data, visualization is rendered */}
          {simulationData && <Sattellites data={simulationData} />}
        </Suspense>
        <OrbitControls minDistance={2} maxDistance={20} enablePan={false}/>
      </Canvas>
    </div>
  )
}

export default App