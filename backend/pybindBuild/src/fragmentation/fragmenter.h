#pragma once
#include <vector>
#include <cstdint>
#include <cstddef>

std::vector<std::vector<uint8_t>>fragmentData(const std::vector<uint8_t>& data, size_t fragmentSize);
