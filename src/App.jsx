import { useState, useEffect } from 'react'
import './App.css'
import Galaxy from "./Galaxy.jsx";
import * as THREE from 'three';

function App() {
  useEffect(() => {
    
    import("./earth.js");
    
     }, []);

  return (
    <>
      <div className="galaxy-root">
        <Galaxy />
      </div>
      <div id="sphere-container"></div>
      
    </>
  )
}

export default App
