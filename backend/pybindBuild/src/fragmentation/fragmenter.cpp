#include "fragmenter.h"
#include <vector>
#include <cstdint>
#include <algorithm>

std::vector<std::vector<uint8_t>>fragmentData(const std::vector<uint8_t>& data, size_t fragmentSize) {
    std::vector<std::vector<uint8_t>> fragments;        //stores fragments
    for (size_t i = 0; i < data.size(); i += fragmentSize) {        //it advances fragmentSize by fragmentSize
        size_t end = std::min(i + fragmentSize, data.size());       //avoids going over the edge since the last fragment could be smaller
        fragments.emplace_back(data.begin() + i, data.begin() + end);       //creates and copies fragments with ranges
    }
    return fragments;
}
