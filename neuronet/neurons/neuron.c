#include "neuron.h"
#include "utils.h"
#include "neuron_linear.c"
#include "neuron_poly.c"
#include "neuron_pattern.c"

void neuron_create(neuron_t *n, neuron_description_t *info) {
    switch(info->n_type) {
        case Linear:
            neuron_linear_create(n, info->num_inputs);
            break;
        case Poly:
            neuron_poly_create(n, info->num_inputs);
            break;
        case Pattern:
            neuron_pattern_create(n, info->num_inputs);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", info->n_type);
    }
    for(uint32_t i=0; i<info->num_inputs; i++) {
        n->input_indices[i] = info->indices[i];
    }
}

// Use array[array_idx] as input[input_idx]
void neuron_set_input_idx(neuron_t *n, uint32_t input_idx, uint32_t array_idx) {
    if(input_idx >= n->num_inputs)
        RAISE("Error: Input index %d is greater than the number of inputs %d\n", input_idx, n->num_inputs);
    n->input_indices[input_idx] = array_idx;
}

void neuron_set_coeff(neuron_t *n, uint32_t idx, double value) {
    if(idx >= n->num_coeffs)
        RAISE("Error: Index %d is greater than the number of coefficients %d\n", idx, n->num_coeffs);
    n->coeffs[idx] = value;
}

void neuron_set_coeffs(neuron_t *n, double *values) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        n->coeffs[i] = values[i];
    }
}

char * neuron_get_coeffs(neuron_t *n) {
    char *coeffs = doubles_to_string(n->coeffs, n->num_coeffs);
    // printf("Neuron coeffs: [");
    // for(uint32_t i=0; i<n->num_coeffs; i++) {
    //     printf("%f, ", n->coeffs[i]);
    // }
    // printf("]\n");
    // printf("Neuron coeffs: %s\n", coeffs);
    return coeffs;
}

double neuron_get_coeff(neuron_t *n, uint32_t idx) {
    return n->coeffs[idx];
}

double neuron_get_output(neuron_t *n, double *inputs) {
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->inputs[i] = inputs[n->input_indices[i]];
    }
    switch(n->type) {
        case Linear:
            return neuron_linear_get_output(n);
        case Poly:
            return neuron_poly_get_output(n);
        case Pattern:
            return neuron_pattern_get_output(n);
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

double activation_func(double value) {
    if(value >= 1.0)
        return 1.0;
    if(value <= -1.0)
        return -1.0;
    return value;
}
