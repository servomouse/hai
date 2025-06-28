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
    double *inputs;
    uint32_t *input_indices;
    uint32_t num_inputs;
    double *coeffs;
    uint32_t num_coeffs;
    // Mutations feature:
    double *coeffs_backup;
    double *coeffs_delta;
    uint8_t mutated;
    uint32_t bad_mutations_counter;
    double mutation_step;
    // !Mutations feature
    double output;
    neuron_type_t type;
} neuron_t;
