#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint32_t neuron_type_t;

enum neuron_type {
    Linear = 0,
    Poly,
    Pattern,
    Neuron_types_num,   // Keep me last
};

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

typedef struct {
    uint32_t idx;
    uint32_t num_inputs;
    neuron_type_t n_type;
    uint32_t output_idx;    // set to -1 for a neuron thet is not connected to the output
    uint32_t indices[0];
} neuron_description_t;
