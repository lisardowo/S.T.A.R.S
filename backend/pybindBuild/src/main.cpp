#include <iostream>
#include "file_io/reader.h"
#include "file_io/writer.h"
#include "compression/lz4_wrapper.h"
#include <vector>
#include <cstdint>
#include "fragmentation/fragmenter.h"
#include "fragmentation/xor_coder.h"
#include "utils/checksum.h"
#include "lz4.h"
#include <chrono>

int main() {
    auto data = readFile("data/input/telemetry.csv");       //telemetry into "data"
    auto start = std::chrono::high_resolution_clock::now();      //timers using computer ticks 
    auto compressed = compressBlock(data);      //compressed data
    auto mid = std::chrono::high_resolution_clock::now();      
    std::vector<uint8_t> compressedBytes(compressed.begin(), compressed.end());      //lz4 uses char, modules use uint8  
    size_t fragmentSize = 64 * 1024;
    auto fragments = fragmentData(compressedBytes, fragmentSize);
    uint32_t checksum = calculateChecksum(compressedBytes);
    std::vector<std::vector<uint8_t>> xorFragments;
    for (size_t i = 0; i + 1 < fragments.size(); i += 2) {
        xorFragments.push_back(xorBlocks(fragments[i], fragments[i + 1]));
    }
    auto decompressed = decompressBlock(compressed, data.size());       //decompressed data
    auto end = std::chrono::high_resolution_clock::now();
    writeFile("data/output/reconstructed.csv", decompressed);

    auto compressionTime = std::chrono::duration_cast<std::chrono::microseconds>(mid - start).count();      //duration_cast converts the ticks into us (microseconds)
    auto decompressionTime = std::chrono::duration_cast<std::chrono::microseconds>(end - mid).count();      //they also time how long it takes to compress and decompress

    std::cout << "Original size: " << data.size() << " bytes\n";
    std::cout << "Compressed size: " << compressed.size() << " bytes\n";
    double ratio = static_cast<double>(compressed.size()) / data.size() * 100.0;
    std::cout << "Compression ratio: " << ratio << "%\n";
    std::cout << "Compression time: " << compressionTime << " us\n";
    std::cout << "Decompression time: " << decompressionTime << " us\n";
    std::cout << "Checksum: " << checksum << "\n";
    std::cout << "Fragments: " << fragments.size() << "\n";
    std::cout << "XOR blocks: " << xorFragments.size() << "\n";
    return 0;
}
