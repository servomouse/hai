#include "utils.h"

// Creates an array like this: {-0.123457, 0.987654, -0.456789}
// Fails on error, no need to check if the result is NULL
char* doubles_to_string(const double* array, uint32_t length) {
    uint32_t base_size = length * 9 + (length > 1 ? 2 *(length - 1) : 0);
    size_t buffer_size = 2 + base_size + 1;
    char* output = (char*)malloc(buffer_size);
    
    if (output == NULL) {
        RAISE("Memory allocation failed");
    }

    char* ptr = output;
    ptr += sprintf(ptr, "{");

    for (size_t i = 0; i < length; i++) {
        ptr += sprintf(ptr, "%.6f", array[i]);
        if (i < length - 1) {
            ptr += sprintf(ptr, ", ");
        }
    }

    sprintf(ptr, "}");
    return output;
}
