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
    double error_sum;
    uint32_t counter;
} backprop_error_t;

typedef struct {
    double *inputs;
    uint32_t *input_indices;
    uint32_t num_inputs;
    void *coeffs;
    uint32_t num_coeffs;
    // Mutations feature:
    double *coeffs_backup;
    double *coeffs_delta;
    backprop_error_t *bp_deltas;
    // !Mutations feature
    double weighted_sum;    // Needed for backpropagation
    double output;
    neuron_type_t type;
} neuron_t;

typedef struct __attribute__((packed)) {
    uint32_t desc_size;
    uint32_t idx;
    uint32_t num_inputs;
    neuron_type_t n_type;
    // uint32_t output_idx;    // set to -1 for a neuron thet is not connected to the output
    uint32_t indices[0];
} neuron_description_t;
