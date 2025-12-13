import { useState, useEffect } from 'react'
import './App.css'
import Galaxy from "./Galaxy.jsx";


function App() {
  useEffect(() => {
    
    import("./earth.js");
    
     }, []);

  return (
    <>
      <div className="galaxy-root">
       < 
        Galaxy
        mouseRepulsion={false}
        mouseInteraction={false}
        density={2}
        glowIntensity={0.5}
        saturation={0.8}
        hueShift={120}
      />
      </div>
      <div id="sphere-container"></div>
      
    </>
  )
}

export default App