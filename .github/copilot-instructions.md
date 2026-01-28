# Copilot Instructions for S.T.A.R.S

Use this guide to be immediately productive in this repo. Focus on the concrete architecture, workflows, and patterns already present.

## Architecture Overview
- Backend: FastAPI service in [backend/server.py](backend/server.py) with CORS. Loads DRL model on `startup` and exposes `GET /health` and `POST /api/transmit`.
- Routing/DRL: Core logic in [backend/DRL-router/router.py](backend/DRL-router/router.py), using `GMTS_Agent`, `SatelliteTrainer`, and `IntelligentRouter`. The router computes candidate paths and ratios; do not rename Spanish keys like `enlaces`.
- Simulation: Packet flow via SimPy in [backend/transmisor.py](backend/transmisor.py). `TransmissionSimulator.process_and_send()` compresses, fragments, selects routes, simulates hops, and returns a JSON with `meta`, `routes`, and `timeline`.
- C++ module: Pybind11 extension `cpp_core` in [backend/pybindBuild/src](backend/pybindBuild/src) provides `compress(bytes) -> bytes` and `fragment(bytes, chunk_size) -> List[bytes]`.
- Frontend: React/Vite app under [src/](src/) rendering Earth and satellites ([src/Satellites.jsx](src/Satellites.jsx), [src/earth.jsx](src/earth.jsx)). Talks to the backend via HTTP.

## Data Flow (API `POST /api/transmit`)
- Upload file → read bytes → decode to text if possible → initialize SimPy `Environment` and `ConstellationManager`.
- Use global `IntelligentRouter` (model loaded at startup) bound to the new constellation.
- `TransmissionSimulator` → `cpp_core.compress` → `cpp_core.fragment(…, 1024)` → route assignment by DRL ratios → hop-by-hop simulation → returns JSON for frontend animation.

## Developer Workflows
- Backend (Linux):
  - Create/activate venv and install deps in [backend/requirements.txt](backend/requirements.txt).
  - Build `cpp_core` locally (required for performance): in [backend/pybindBuild/src](backend/pybindBuild/src), run `pip install .` (system `liblz4` and C++17 toolchain must be present).
  - Run: `python backend/server.py` (uses uvicorn when executed as main).
  - Quick checks:
    - Health: `curl http://localhost:8000/health` → `{"status":"ok"}`.
    - Transmit: `curl -F "file=@backend/pybindBuild/data/input/telemetry.csv" http://localhost:8000/api/transmit`.
- Frontend:
  - `npm install` at repo root, then `npm run dev` → http://localhost:5173.

## Conventions and Patterns
- Path imports: backend files add `DRL-router` to `sys.path`; keep module layout stable and avoid moving this folder without updating that path.
- Router outputs:
  - Candidate routes with fields: `enlaces` (list of `"Sx_y-Sa_b"`), `estrategia`, plus computed `delay`, `throughput`, `max_load`.
  - Feature vectors: `[hops/10, delay*10, throughput/1000, max_load]`.
- Timelines for UI: `TransmissionSimulator.transmission_log` collects chronological events of type `PACKET_START` and `PACKET_HOP` with `time`, `route_idx`, `packet_id`, and `location`.
- Model file: Pretrained weights at [backend/DRL-router/mejorModelo/best_model.pth](backend/DRL-router/mejorModelo/best_model.pth); loaded automatically if present.
- CUDA: Router uses `cuda` if available, else `cpu`; avoid hardcoding device.

## Integration Notes
- C++ build requirements: `liblz4` headers and a C++17 compiler. See README Backend Setup for exact commands. Prefer `pip install .` to place `cpp_core` in site-packages so `transmisor.py` can import it.
- SimPy environment: Instantiate a fresh `simpy.Environment()` per transmission to reset time (`env.now == 0`).
- CORS: Allowed origins are listed in [backend/server.py](backend/server.py); match frontend dev URL.

## Safe Changes Examples
- Add an API endpoint: follow the pattern in [backend/server.py](backend/server.py) and return JSON similar to `process_and_send()` result.
- Extend `cpp_core`: add new functions in [backend/pybindBuild/src/bindings.cpp](backend/pybindBuild/src/bindings.cpp), update [backend/pybindBuild/src/setup.py](backend/pybindBuild/src/setup.py), then `pip install .`.
- Modify routing: adjust feature computation in `IntelligentRouter._extract_path_metrics()` and keep returned keys (`delay`, `throughput`, `max_load`) to avoid breaking consumers.

If any part is unclear (e.g., DRL training workflow, telemetry formats, or expected frontend event schema), tell us what you need clarified and we’ll refine this file.
