#include <fstream>
#include <vector>  
#include <string>
#include "writer.h"


void writeFile(const std::string& path, const std::vector<char>& data) {
    std::ofstream file(path, std::ios::binary);
    file.write(data.data(), data.size());
}
