
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "DRL-router"))

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import simpy
import shutil

#TODO agreggar /health endpoint para confirmar el backend corriendo
from transmisor import TransmissionSimulator
from satelites import ConstellationManager
from router import IntelligentRouter

app = FastAPI()

ALLOWED_ORIGINS = [

    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "https://s-t-a-r-s.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

global_router = None
global_constellation_template = None

@app.get("/health")
def health():
    return {"status" : "ok"}


@app.on_event("startup")
def load_model():
    """Carga el modelo DRL y la constelación base al iniciar el servidor"""
    global global_router, global_constellation_template
    print("[API] Cargando modelo DRL y sistema...")
    
    # Entorno temporal para inicializar el enviroment
    temp_env = simpy.Environment()
    manager = ConstellationManager(temp_env)
    
    # Router en modo inferencia 
    global_router = IntelligentRouter(manager, train_mode=False)
    print("[API] API cargada.")



@app.post("/api/transmit")

async def passData(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()

        try:
            information = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Por ahora fuerza una representación string de todo binario puro  (zip/imagen)
            #TODO modificar transmission.py para aceptar bytes puros
            information = str(content_bytes)
        
        print(f"[API] Archivo Procesado: {file.filename} ({len(content_bytes)} bytes)")

        env = simpy.Environment()
        
        # IMPORTANTE: ConstellationManager debe recrearse o resetearse para cada simulación
        # para que el tiempo (env.now) empiece en 0.
        constellation = ConstellationManager(env)
        
        
        global_router.constellation = constellation
        
        # Inicializar simulador
        simulator = TransmissionSimulator(env, constellation, global_router)
        
        
        src_p, src_s = 0, 0
        dst_p, dst_s = 2, 5 #TODO importar NP y NS de constellation manager para generar proceduralmente la cantidad de planos y satelites
                            #Tambien podria declararse eso localmente dado que somos nosotros quienes le pasan el parametro
                            #o finalmente podria ser pasado por el front como un parametro
        
        # process_and_send debe ser adaptado ligeramente para devolver el valor al terminar
        proc = env.process(simulator.process_and_send(information, src_p, src_s, dst_p, dst_s))
        env.run(until=proc) # Correr hasta que termine el proceso
       
    
        
        result_json = proc.value
        
       
        result_json['meta']['filename'] = file.filename
        
        return result_json

    except Exception as e:
        print(f"[API Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)