
#include "xor_coder.h"
#include <algorithm> 

std::vector<uint8_t>xorBlocks(const std::vector<uint8_t>& a, const std::vector<uint8_t>& b) {      //used to recover corrupted or lost fragments using xor as a "key"
    size_t size = std::min(a.size(), b.size());     //both fragments have to be the same size, size_t used as standard
    std::vector<uint8_t> result(size);      //stores xor blocks
    for (size_t i = 0; i < size; ++i) {     //xor
        result[i] = a[i] ^ b[i];
    }
    return result;
}

