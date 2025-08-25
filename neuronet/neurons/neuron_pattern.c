#include "neuron.h"

void neuron_pattern_create(neuron_t *n, uint32_t num_inputs) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

double neuron_pattern_get_output(neuron_t *n, double *inputs) {
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->inputs[i] = inputs[n->input_indices[i]];
    }
    RAISE("Error: Pattern neuron not implemented!\n");
}

char *neuron_pattern_get_coeffs(neuron_t *n) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

void neuron_pattern_set_coeffs(neuron_t *n, double *values) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

void neuron_pattern_set_coeff(neuron_t *n, uint32_t idx,double value) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

/* MUTATIONS */

// The opposite is neuron_rollback
void neuron_pattern_stash_state(neuron_t * n) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

void neuron_pattern_mutate(neuron_t * n, double mutation_step) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

// The opposite is neuron_stash_state
void neuron_pattern_rollback(neuron_t * n) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

/* BACKPROPAGATION */

void neuron_pattern_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    RAISE("Error: Pattern neuron not implemented!\n");
}

void neuron_pattern_backprop_update_weights(neuron_t *n, double learning_rate) {
    RAISE("Error: Pattern neuron not implemented!\n");
}
