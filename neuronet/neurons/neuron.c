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

char *neuron_get_coeffs(neuron_t *n) {
    switch(n->type) {
        case Linear:
            return neuron_linear_get_coeffs(n);
            break;
        case Poly:
            return neuron_poly_get_coeffs(n);
            break;
        case Pattern:
            return neuron_pattern_get_coeffs(n);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

void neuron_set_coeffs(neuron_t *n, double *values) {
    switch(n->type) {
        case Linear:
            neuron_linear_set_coeffs(n, values);
            break;
        case Poly:
            neuron_poly_set_coeffs(n, values);
            break;
        case Pattern:
            neuron_pattern_set_coeffs(n, values);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
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

double control_coeffs_func(double coeff) {
    if(coeff > 1.0) {
        return 1.0;
    } else if(coeff < -1.0) {
        return -1.0;
    } else {
        return round_to_precision(coeff, 6);
    }
}
// The opposite is neuron_rollback
void neuron_stash_state(neuron_t * n) {
    switch(n->type) {
        case Linear:
            neuron_linear_stash_state(n);
            break;
        case Poly:
            neuron_poly_stash_state(n);
            break;
        case Pattern:
            neuron_pattern_stash_state(n);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

void neuron_mutate(neuron_t * n, double mutation_step) {
    switch(n->type) {
        case Linear:
            neuron_linear_mutate(n, mutation_step);
            break;
        case Poly:
            neuron_poly_mutate(n, mutation_step);
            break;
        case Pattern:
            neuron_pattern_mutate(n, mutation_step);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

// The opposite is neuron_stash_state
void neuron_rollback(neuron_t * n) {
    switch(n->type) {
        case Linear:
            neuron_linear_rollback(n);
            break;
        case Poly:
            neuron_poly_rollback(n);
            break;
        case Pattern:
            neuron_pattern_rollback(n);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

void neuron_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    switch(n->type) {
        case Linear:
            neuron_linear_backpropagate(n, errors, self_idx);
            break;
        case Poly:
            neuron_poly_backpropagate(n, errors, self_idx);
            break;
        case Pattern:
            neuron_pattern_backpropagate(n, errors, self_idx);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

void neuron_backprop_update_weights(neuron_t *n, double learning_rate) {
    switch(n->type) {
        case Linear:
            neuron_linear_backprop_update_weights(n, learning_rate);
            break;
        case Poly:
            neuron_poly_backprop_update_weights(n, learning_rate);
            break;
        case Pattern:
            neuron_pattern_backprop_update_weights(n, learning_rate);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}
