// Ejemplo de función en React
const handleFileUpload = async (file) => {
  const formData = new FormData();
  formData.append("file", file); // 'file' debe coincidir con el nombre en FastAPI

  try {
    const response = await fetch("http://localhost:8000/api/transmit", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Error en la transmisión");

    const data = await response.json();
    
    console.log("Datos recibidos:", data);
    // Aquí llaman a la función de Three.js pasándole data.routes y data.timeline
    startSatelliteAnimation(data); 

  } catch (error) {
    console.error("Error:", error);
  }
};