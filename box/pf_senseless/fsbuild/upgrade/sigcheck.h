#pragma once

#include <stdint.h>
#include <stdbool.h>

bool validate_signature(const uint8_t signature[256], const unsigned char hash[20]);
