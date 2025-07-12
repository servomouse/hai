#include "neuron.h"

void neuron_poly_create(neuron_t *n, uint32_t num_inputs) {
    RAISE("Error: Poly neuron not implemented!\n");
}

double neuron_poly_get_output(neuron_t *n) {
    RAISE("Error: Poly neuron not implemented!\n");
}

char *neuron_poly_get_coeffs(neuron_t *n) {
    RAISE("Error: Poly neuron not implemented!\n");
}

void neuron_poly_set_coeffs(neuron_t *n, double *values) {
    RAISE("Error: Poly neuron not implemented!\n");
}

/* MUTATIONS */

// The opposite is neuron_rollback
void neuron_poly_stash_state(neuron_t * n) {
    RAISE("Error: Poly neuron not implemented!\n");
}

void neuron_poly_mutate(neuron_t * n, double mutation_step) {
    RAISE("Error: Poly neuron not implemented!\n");
}

// The opposite is neuron_stash_state
void neuron_poly_rollback(neuron_t * n) {
    RAISE("Error: Poly neuron not implemented!\n");
}
