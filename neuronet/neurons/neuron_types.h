#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef enum {
    Linear = 0,
    Poly,
    Pattern,
} neuron_type_t;

typedef struct {
    double * inputs;
    uint32_t num_inputs;
    double * coeffs;
    uint32_t num_coeffs;
    double output;
    neuron_type_t type;
} neuron_t;
