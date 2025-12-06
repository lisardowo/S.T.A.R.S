import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Galaxy from './Galaxy.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Galaxy
    mouseRepulsion={false}

    mouseInteraction={true}

    density={2}

    glowIntensity={0.5}

    saturation={0.8}

    hueShift={120}
    
    />
    <App />
  </StrictMode>,
)
