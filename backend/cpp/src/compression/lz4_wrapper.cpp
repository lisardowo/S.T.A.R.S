#include "lz4_wrapper.h"
#include "../../external/lz4/lib/lz4.h"

std::vector<char>compressBlock(const std::vector<char>& input) {        //compression
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

std::vector<char>decompressBlock(const std::vector<char>& compressed, int originalSize) {       //decompression
    std::vector<char> output(originalSize);
    LZ4_decompress_safe(
        compressed.data(),
        output.data(),
        compressed.size(),
        originalSize
    );
    return output;
}
