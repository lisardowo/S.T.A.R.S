from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

# Nombre del módulo (como se importará en Python)
MODULE_NAME = "cpp_core"

# Lista de archivos fuente (.cpp)
sources = [
    "bindings.cpp",
    "compression/lz4_wrapper.cpp",
    "fragmentation/fragmenter.cpp",
    "fragmentation/xor_coder.cpp",
]

# Configuración de la extensión (usa Pybind11Extension para añadir los includes automáticamente)
ext_modules = [
    Pybind11Extension(
        MODULE_NAME,
        sources,
        include_dirs=["compression", "fragmentation"],
        libraries=["lz4"],  # Requiere liblz4 en el sistema (liblz4-dev)
        language="c++",
        extra_compile_args=["-std=c++17", "-O3"],
    ),
]

setup(
    name=MODULE_NAME,
    version="0.1",
    author="Pavel",
    description="Modulo de transmision satelital optimizado en C++",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)