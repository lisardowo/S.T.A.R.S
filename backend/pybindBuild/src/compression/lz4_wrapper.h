#pragma once
#include <vector>

std::vector<char> compressBlock(const std::vector<char>& input);
std::vector<char> decompressBlock(
    const std::vector<char>& compressed,
    int originalSize
);
