#include "neuron.h"

void neuron_temp_create(neuron_t *n, uint32_t num_inputs) {
    n->type = Temporal;
    n->num_inputs = num_inputs;
    n->num_coeffs = num_inputs+1;
    n->inputs = (double*)calloc(n->num_inputs, sizeof(double));
    n->prev_inputs = (double*)calloc(n->num_inputs, sizeof(double));
    n->input_indices = (uint32_t*)calloc(n->num_inputs, sizeof(uint32_t));
    n->coeffs = calloc(n->num_coeffs, sizeof(double));
    n->coeffs_backup = calloc(n->num_coeffs, sizeof(double));
    n->coeffs_delta = calloc(n->num_coeffs, sizeof(double));
    n->bp_deltas = calloc(n->num_coeffs, sizeof(backprop_error_t));
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = random_double(-0.1, 0.1);
    }
}

double neuron_temp_get_output(neuron_t *n, double *inputs) {
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->inputs[i] = activation_func(inputs[n->input_indices[i]] - n->prev_inputs[i]);
    }
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->prev_inputs[i] = inputs[n->input_indices[i]];
    }
    n->weighted_sum = ((double*)n->coeffs)[n->num_coeffs-1]; // BIAS
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->weighted_sum += n->inputs[i] * ((double*)n->coeffs)[i];
    }
    n->output = activation_func(n->weighted_sum);
    return n->output;
}

char *neuron_temp_get_coeffs(neuron_t *n) {
    char *coeffs = doubles_to_string((double*)n->coeffs, n->num_coeffs);
    return coeffs;
}

void neuron_temp_set_coeffs(neuron_t *n, double *values) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = values[i];
    }
}

/* MUTATIONS */

// The opposite is neuron_rollback
void neuron_temp_stash_state(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs_backup)[i] = ((double*)n->coeffs)[i];
    }
}

void neuron_temp_mutate(neuron_t * n, double mutation_step) {
    neuron_linear_stash_state(n);
    gen_vector(n->num_coeffs, random_double(0, mutation_step), (double*)n->coeffs_delta);
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = control_coeffs_func(
            ((double*)n->coeffs)[i] + ((double*)n->coeffs_delta)[i]
        );
    }
}

// The opposite is neuron_stash_state
void neuron_temp_rollback(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = ((double*)n->coeffs_backup)[i];
    }
}

/* BACKPROPAGATION */

void neuron_temp_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    RAISE("Error: Temporal neuron not implemented!\n");
}

void neuron_temp_backprop_update_weights(neuron_t *n, double learning_rate) {
    RAISE("Error: Temporal neuron not implemented!\n");
}
