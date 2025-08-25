#pragma once

#include <stdint.h>
#include "neuron_types.h"

typedef struct {
    uint32_t num_inputs;
    double *core_inputs;
    uint32_t lateral_num_links;
    uint32_t lateral_num_inputs;
    double *lateral_inputs;
    double *lateral_outputs;
    double *core_outputs;
    double *arr;
    neuron_t *neurons;
    backprop_error_t *feedback;
} ucore_t;
