#include "checksum.h"
#include <cstdint>
#include <vector>

uint32_t calculateChecksum(const std::vector<uint8_t>& data) {      //adds up bytes on the file to see if the restored version was successful
    uint32_t checksum = 0;                          //standard 32 bit unsigned int for storing positive data
    for (uint8_t byte : data) {                                             
        checksum += byte;                           //checksum = "identity" key
    }
    return checksum; 
}
