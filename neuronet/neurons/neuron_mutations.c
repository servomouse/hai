#include "neuron.h"
#include "utils.h"
#include "mymath.h"

static double control_coeffs_func(double coeff) {
    if(coeff > 1.0) {
        return 1.0;
    } else if(coeff < -1.0) {
        return -1.0;
    } else {
        return coeff;
    }
}

// The opposite is neuron_rollback
void neuron_stash_state(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        n->coeffs_backup[i] = n->coeffs[i];
    }
}

void neuron_mutate(neuron_t * n, double mutation_step) {
    neuron_stash_state(n);
    gen_vector(n->num_coeffs, random_double(0, mutation_step), n->coeffs_delta);
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        n->coeffs[i] = control_coeffs_func(n->coeffs[i] + n->coeffs_delta[i]);
    }
}

// The opposite is neuron_stash_state
void neuron_rollback(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        n->coeffs[i] = n->coeffs_backup[i];
    }
}
