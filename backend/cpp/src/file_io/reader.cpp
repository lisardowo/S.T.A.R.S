#include "reader.h"
#include <fstream>
#include <vector>
#include <iterator> 

std::vector<char> readFile(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    return std::vector<char>(
        (std::istreambuf_iterator<char>(file)),
        std::istreambuf_iterator<char>()
    );
}

