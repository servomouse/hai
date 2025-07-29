#pragma once

#include <stdint.h>
#include "neuron_types.h"

typedef struct {
    uint32_t num_inputs;
    uint32_t net_size;      // Total size of the net (num_inputs + num_neurons)
    uint32_t num_outputs;
    neuron_description_t *neurons;
} network_map_t;

typedef struct {
    uint32_t num_items;
    char **items;
} net_coeffs_t;

typedef struct {
    uint8_t is_micronet;
    uint32_t num_inputs;
    uint32_t num_neurons;
    uint32_t num_outputs;
    uint32_t size;
    double *arr;
    backprop_error_t *bp_errors;    // Errors for back propagation
    double *input_errors;
    neuron_t *neurons;
    uint32_t *output_indices;
    double *outputs;
    uint32_t mutated_neuron_idx;
    // uint32_t num_micronets;
    // struct network_t **micronets;
} network_t;
