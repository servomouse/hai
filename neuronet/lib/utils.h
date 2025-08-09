#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#ifdef __unix__
    #define DLL_PREFIX 
#elif defined(_WIN32) || defined(WIN32)
    #define DLL_PREFIX __declspec(dllexport)
#endif

#define RAISE(msg, ...) {printf(msg " (line %d in file %s)\n", ##__VA_ARGS__, __LINE__, __FILE__); fflush(stdout); exit(EXIT_FAILURE);}

// Creates an array like this: {-0.123457, 0.987654, -0.456789}
// Fails on error, no need to check if the result is NULL. Free the result after use
char* doubles_to_string(const double* array, uint32_t length);
char* complex_to_string(const void* array, uint32_t num_dimensions, uint32_t length);
