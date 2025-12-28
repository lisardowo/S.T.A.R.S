#include <iostream>
#include "file_io/reader.h"
#include "file_io/writer.h"
#include <vector>
#include "lz4.h"
#include <chrono>


std::vector<char> compressBlock(const std::vector<char>& input) {
    int maxSize = LZ4_compressBound(input.size());
    std::vector<char> compressed(maxSize);

    int compressedSize = LZ4_compress_default(
        input.data(),
        compressed.data(),
        input.size(),
        maxSize
    );

    compressed.resize(compressedSize);
    return compressed;
}

std::vector<char> decompressBlock(
    const std::vector<char>& compressed,
    int originalSize
) {
    std::vector<char> output(originalSize);

    LZ4_decompress_safe(
        compressed.data(),
        output.data(),
        compressed.size(),
        originalSize
    );

    return output;
}


int main() {
    auto data = readFile("data/input/telemetry.csv");
    auto compressed = compressBlock(data);
    auto decompressed = decompressBlock(compressed, data.size());
    writeFile("data/output/reconstructed.csv", decompressed);
    auto start = std::chrono::high_resolution_clock::now();
    auto mid = std::chrono::high_resolution_clock::now();
    auto end = std::chrono::high_resolution_clock::now();
    auto compressTime = std::chrono::duration_cast<std::chrono::microseconds>(mid - start).count();
    auto decompressTime = std::chrono::duration_cast<std::chrono::microseconds>(end - mid).count();

    std::cout << "Original size: " << data.size() << " bytes\n";
    std::cout << "Compressed size: " << compressed.size() << " bytes\n";
    std::cout << "Compression ratio: "
          << (100.0 * compressed.size() / data.size()) << "%\n";
    std::cout << "Compress time: " << compressTime << " us\n";
    std::cout << "Decompress time: " << decompressTime << " us\n";

    return 0;
}
