#pragma once

#include <stdint.h>
#include "neuron_types.h"

typedef struct {
    uint32_t idx;
    uint32_t num_inputs;
    neuron_type_t n_type;
    uint32_t indices[0];
} neuron_description_t;

typedef struct {
    uint32_t num_inputs;
    uint32_t num_neurons;
    uint32_t *neurons;  // neuron_description_t is used here
    uint32_t num_outputs;
    uint32_t output_indices[];
} network_map_t;

typedef struct network_t {
    uint8_t is_micronet;
    uint32_t num_inputs;
    uint32_t num_neurons;
    uint32_t net_size;
    uint32_t num_outputs;
    uint32_t *output_indices;
    double *arr;
    double *outputs;
    neuron_t *neurons;
    uint32_t mutated_neuron_idx;
    network_map_t *map;
    struct network_t * micronets;
} network_t;
