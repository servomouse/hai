#include "utils.h"

// Creates an array like this: {-0.123457, 0.987654, -0.456789}
// Free after use
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

typedef struct {
    double val[2];
} complex_2d_val_t;

typedef struct {
    double val[3];
} complex_3d_val_t;

// Creates an array like this: {-0.123457, 0.987654, -0.456789}
// Free after use
// Fails on error, no need to check if the result is NULL
char* complex_to_string(const void* array, uint32_t num_dimensions, uint32_t length) {
    uint32_t item_length = 9 * num_dimensions;
    uint32_t base_size = (length * item_length) + (length > 1 ? 2 *(length - 1) : 0);
    size_t buffer_size = 2 + base_size + 1;
    char* output = (char*)malloc(buffer_size);
    
    if (output == NULL) {
        RAISE("Memory allocation failed");
    }

    char* ptr = output;
    ptr += sprintf(ptr, "{");

    switch(num_dimensions) {
        case 1:
            for (size_t i = 0; i < length; i++) {
                ptr += sprintf(ptr, "%.6f", ((double*)array)[i]);
                if (i < length - 1) {
                    ptr += sprintf(ptr, ", ");
                }
            }
            break;
        case 2:
            for (size_t i = 0; i < length; i++) {
                ptr += sprintf(ptr, "%.6f", ((complex_2d_val_t*)array)[i].val[0]);
                ptr += sprintf(ptr, ", ");
                ptr += sprintf(ptr, "%.6f", ((complex_2d_val_t*)array)[i].val[1]);
                if (i < length - 1) {
                    ptr += sprintf(ptr, ", ");
                }
            }
            break;
        case 3:
            for (size_t i = 0; i < length; i++) {
                ptr += sprintf(ptr, "%.6f", ((complex_2d_val_t*)array)[i].val[0]);
                ptr += sprintf(ptr, ", ");
                ptr += sprintf(ptr, "%.6f", ((complex_2d_val_t*)array)[i].val[1]);
                ptr += sprintf(ptr, ", ");
                ptr += sprintf(ptr, "%.6f", ((complex_3d_val_t*)array)[i].val[2]);
                if (i < length - 1) {
                    ptr += sprintf(ptr, ", ");
                }
            }
            break;
        default:
            RAISE("Error: Unknown number of dimensions: %d", num_dimensions);
    }

    sprintf(ptr, "}");
    return output;
}
