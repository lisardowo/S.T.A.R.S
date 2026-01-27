# S.T.A.R.S - Satelite and Telecomunication Automatic Relay System

A student-built tool designed to optimize satellite communication routing using Deep Reinforcement Learning. Built during a hackathon with the theme "ORBIT."

## Team Members

Lisardo Sobrado Morales, Jorge Alberto Rivera Ahumada , Pavel Bautista Fuentes, Diego del Rio Pulido 

## Overview

S.T.A.R.S (Satellite and Telecomunication Automatic Relay System) combines deep reinforcement learning with satellite communication routing to provide intelligent traffic management and optimization. The system:
- Simulates satellite networks and orbital mechanics
- Uses DRL agents to optimize routing decisions
- Provides real-time telemetry monitoring and analysis
- Generates fragmented and compressed data packets for efficient transmission
- Visualizes satellite networks in an interactive 3D interface

## Features

- **DRL-Based Routing**: Advanced Deep Reinforcement Learning model for intelligent satellite routing
- **Satellite Simulation**: Accurate simulation of satellite positions and orbital mechanics
- **Data Optimization**: 
  - LZ4 compression for efficient data transfer
  - XOR-based fragmentation and error correction
  - Checksum validation for data integrity
- **Real-Time Monitoring**: Live telemetry tracking and performance metrics
- **Interactive 3D Visualization**: React-based visualization of satellite networks and Earth
- **Flexible Configuration**: Configurable satellite parameters and routing policies
- **Multi-Format Support**: CSV telemetry input with reconstructed output

## Project Structure

```
S.T.A.R.S/
├── backend/                    # Python backend server
│   ├── server.py              # Main FastAPI server
│   ├── transmisor.py          # Transmission handling
│   ├── requirements.txt        # Python dependencies
│   └── DRL-router/            # Deep RL routing module
│       ├── router.py          # Routing algorithm
│       ├── satelites.py       # Satellite simulation
│       ├── monitor.py         # Performance monitoring
│       ├── formulas.py        # Orbital mechanics
│       └── mejorModelo/       # Pre-trained DRL model
├── pybindBuild/               # C++ extension for performance
│   ├── src/
│   │   ├── compression/       # LZ4 compression wrapper
│   │   ├── fragmentation/     # Data fragmentation & XOR coding
│   │   ├── file_io/           # File reading/writing
│   │   └── utils/             # Utility functions
│   └── data/
│       ├── input/             # Telemetry input data
│       └── output/            # Reconstructed data
├── src/                        # React frontend
│   ├── App.jsx               # Main application component
│   ├── earth.jsx             # Earth visualization
│   ├── Satellites.jsx        # Satellite visualization
│   ├── main.jsx              # Entry point
│   └── utils.js              # Utility functions
├── public/                    # Static assets
├── package.json               # Node.js dependencies
├── vite.config.js            # Vite configuration
├── eslint.config.js          # ESLint configuration
└── README.md                 # This file
```

## Prerequisites

- **Python 3.8+**: For running the backend server
- **Node.js 16+**: For running the frontend application
- **npm**: Node package manager
- **C++ Compiler**: For building the pybind extensions (optional but recommended)
- **CUDA (Optional)**: For GPU acceleration of DRL training

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Navigate to the project root directory:
   ```bash
   cd ../
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

### Starting the Backend

From the `backend/` directory:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the server
python server.py
```

The backend will be available at `http://localhost:8000`

Verify the backend is running:

#### For local
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```
#### For web
```bash
curl http://s-t-a-r-s.onrender.com/health
# Should return: {"status":"ok"}
```

### Starting the Frontend

From the project root directory:

```bash
# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Using the Application

1. Open your browser and navigate to `http://localhost:5173`
2. View the interactive 3D visualization of satellite networks
3. Monitor real-time telemetry data and routing optimization
4. Analyze DRL agent decisions and performance metrics
5. Adjust satellite parameters and observe routing changes

## API Endpoints

The backend provides the following endpoints:

- `POST /api/transmit` - Process and send data through the constellation

- `GET /health` - Returns the current state of the service (if on or off)


## Technologies Used

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PyTorch**: Deep Reinforcement Learning framework
- **NumPy/SciPy**: Numerical computations and orbital mechanics
- **Pybind11**: C++ Python bindings for performance-critical operations
- **SIMPY**: Simulation of the constellation and satellites modules

### C++ Extensions
- **LZ4**: High-performance compression library
- **XOR Coding**: Forward error correction implementation

### Frontend
- **React**: UI library for interactive components
- **Vite**: Build tool and development server
- **Three.js**: 3D visualization library (via React components)
- **Axios**: HTTP client for API requests

## Development

The project uses:
- DRL agents trained with Deep Q-Networks (DQN) and Policy Gradients
- CORS middleware for frontend-backend communication
- Real-time telemetry stream processing
- Efficient binary data handling with C++ extensions
- Error handling and validation for robust satellite operations

## Contributing

This project was built for students by students. Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation
- Optimize routing algorithms

## AI Tools Disclosure

This project was developed with the assistance of AI tools:

- **Gemini AI**: Mainly as a roadmap and assistance in the topics needed to understand to work in the project
- **GitHub Copilot (GPT-5 model)**: Used for small bugs and questions, also reviewed PR and made tiny patches
- **Claude Sonnet 4.5**: For fine tunning of logic bugs or bad implementation of certain features

The combination of these AI tools helped accelerate development while maintaining code quality and best practices. All AI-generated code was reviewed, corrected and validated by human developers.

## License

This project is open source and available for educational and investigation purposes.

## Acknowledgments

Built during a student hackathon focused on creating technology beyond the earht. The project aims to optimize and stabilice
satellital communication, having a faster and more convenient way to transsmit data that can be used for investigation purposes 

## Future Improvements (Post-Hackathon Roadmap)

To make S.T.A.R.S more robust and closer to a production-ready system, these are the areas we plan to work on after the hackathon:

- API endpoints to implement:
  
   - `POST /route` — Request optimal routing decision from the DRL agent
   - `GET /telemetry` — Get current telemetry data
   - `POST /telemetry/upload` — Upload telemetry CSV file
   - `GET /satellites` — Get current satellite positions
   - `POST /compress` — Compress data using LZ4
   - `POST /fragment` — Fragment and encode data with XOR

- Reconstructed file visualization (for web-demo):
   - Add an interactive preview of the fully reassembled and decompressed payload (text preview, hex dump for binaries), with integrity checks, and a safe download option. Include throughput/latency metrics and per-hop tracing.

- Router logic and architecture:
   - Refactor `IntelligentRouter` into a modular, testable architecture with clear boundaries between policy, environment (`ConstellationManager`), and transport.
   - Provide multiple routing strategies: DRL policy, deterministic heuristic fallback, and hybrid approaches with pluggable reward functions.
   - Constrain for on-board viability (CPU, memory, power) and provide a lightweight inference path suitable for small platforms.
   - Improve simulation realism: TLE-driven orbits, contact windows, link budgets, ground station constraints, and fault injection.
   - Strengthen observability: structured telemetry, per-hop metrics, reproducible scenarios (SimPy seeds), and scenario configuration files.

- CubeSat application :
   - Prototype inter-satellite and satellite-to-ground routing tailored to CubeSat missions.
   - Validate with real TLEs, expected pass schedules, and hardware-in-the-loop tests (e.g., Raspberry Pi/Jetson) to approach flight-like constraints.
   - Explore integration with existing ground station infrastructure and mission operations workflows.

- Reliability and data handling:
   - Extend FEC options beyond XOR, improve checksum strategies, and add adaptive fragmentation based on link conditions.
   - Provide end-to-end integrity and performance reports for each transmission.

- Security and encryption:
   - Implement end-to-end encryption for inter-satellite and satellite-to-ground links to protect sensitive payloads and telemetry.
   - Introduce robust key management (session keys, key rotation, secure provisioning) and evaluate standards like CCSDS Space Data Link Security for applicability.
   - Consider performance and power constraints on small on-board computers to select efficient cryptographic primitives.
   - Motivation: a significant portion of current satellite links operate without encryption, leaving traffic vulnerable to interception and manipulation.

- Milestone outline:
   - v0.1 — Implement missing API endpoints and basic tests
   - v0.2 — Add reconstructed file visualization and integrity reporting
   - v0.3 — Modular router with heuristic fallback and performance baselines
   - v0.4 — CubeSat-focused pilot with hardware-in-the-loop demo
   - v0.4 — Security focused encriptyon system
