#include "neuron.h"
#include "utils.h"
#include "neuron_linear.c"
#include "neuron_poly.c"
#include "neuron_pattern.c"
#include "neuron_temporal.c"

void neuron_map_input(neuron_t *n, uint32_t input_idx, uint32_t net_idx) {
    n->input_indices[input_idx] = net_idx;
}

void neuron_create(neuron_t *n, neuron_description_t *info) {
    neuron_create_simple(n, info->n_type, info->num_inputs);
    for(uint32_t i=0; i<info->num_inputs; i++) {
        n->input_indices[i] = info->indices[i];
    }
}

void neuron_create_simple(neuron_t *n, neuron_type_t n_type, uint32_t num_inputs) {
    switch(n_type) {
        case Linear:
            neuron_linear_create(n, num_inputs);
            break;
        case Poly:
            neuron_poly_create(n, num_inputs);
            break;
        case Pattern:
            neuron_pattern_create(n, num_inputs);
            break;
        case Temporal:
            neuron_temp_create(n, num_inputs);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n_type);
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
        case Temporal:
            return neuron_temp_get_coeffs(n);
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
        case Temporal:
            neuron_temp_set_coeffs(n, values);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

void neuron_set_coeff(neuron_t *n, uint32_t idx, double value) {
    switch(n->type) {
        case Linear:
            neuron_linear_set_coeff(n, idx, value);
            break;
        case Poly:
            neuron_poly_set_coeff(n, idx, value);
            break;
        case Pattern:
            neuron_pattern_set_coeff(n, idx, value);
            break;
        case Temporal:
            neuron_temp_set_coeff(n, idx, value);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

double neuron_get_output(neuron_t *n, double *inputs) {
    switch(n->type) {
        case Linear:
            return neuron_linear_get_output(n, inputs);
        case Poly:
            return neuron_poly_get_output(n, inputs);
        case Pattern:
            return neuron_pattern_get_output(n, inputs);
        case Temporal:
            return neuron_temp_get_output(n, inputs);
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
        case Temporal:
            neuron_temp_stash_state(n);
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
        case Temporal:
            neuron_temp_mutate(n, mutation_step);
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
        case Temporal:
            neuron_temp_rollback(n);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}

void neuron_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    switch(n->type) {
        case Linear:
            neuron_linear_backpropagate_new(n, errors, self_idx);
            break;
        case Poly:
            neuron_poly_backpropagate(n, errors, self_idx);
            break;
        case Pattern:
            neuron_pattern_backpropagate(n, errors, self_idx);
            break;
        case Temporal:
            neuron_temp_backpropagate(n, errors, self_idx);
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
        case Temporal:
            neuron_temp_backprop_update_weights(n, learning_rate);
            break;
        default:
            RAISE("Error: Unknown neuron type: %d\n", n->type);
    }
}
