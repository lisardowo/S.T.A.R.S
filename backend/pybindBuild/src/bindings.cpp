/* bindings.cpp */
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "compression/lz4_wrapper.h"
#include "fragmentation/fragmenter.h"
#include "fragmentation/xor_coder.h"

namespace py = pybind11;

// Adaptadores para convertir bytes de Python a vectores de C++
pybind11::bytes py_compress(const std::string &input) {
    std::vector<char> vec(input.begin(), input.end());
    auto out = compressBlock(vec);
    return py::bytes(std::string(out.begin(), out.end()));
}

std::vector<uint8_t> py_xor(const std::string &a, const std::string &b) {
    std::vector<uint8_t> va(a.begin(), a.end());
    std::vector<uint8_t> vb(b.begin(), b.end());
    return xorBlocks(va, vb);
}

// Fragmentador que devuelve lista de bytes objects a Python
std::vector<py::bytes> py_fragment(const std::string &input, size_t size) {
    std::vector<uint8_t> data(input.begin(), input.end());
    auto fragments = fragmentData(data, size);
    
    std::vector<py::bytes> py_frags;
    for(const auto& frag : fragments) {
        py_frags.push_back(py::bytes(std::string(frag.begin(), frag.end())));
    }
    return py_frags;
}

PYBIND11_MODULE(cpp_core, m) {
    m.doc() = "Modulo de alto rendimiento para transmision satelital";
    
    m.def("compress", &py_compress, "Comprime datos usando LZ4");
    
    m.def("decompress", [](const std::string &input, int originalSize) {
        std::vector<char> vec(input.begin(), input.end());
        auto res = decompressBlock(vec, originalSize);
        return py::bytes(std::string(res.begin(), res.end()));
    }, "Descomprime datos LZ4");

    m.def("fragment", &py_fragment, "Fragmenta datos en bloques");
    
    m.def("xor_blocks", [](const std::string &a, const std::string &b){
         auto res = py_xor(a, b);
         return py::bytes(std::string(res.begin(), res.end()));
    }, "Aplica XOR network coding");
}