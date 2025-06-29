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

void neuron_mutate(neuron_t * n) {
    neuron_stash_state(n);
    
    if(n->mutated == 1) {    // If previuos mutation was successfull, keep going in the same direction
        n->bad_mutations_counter = 0;
    } else {
        if(n->bad_mutations_counter >= 10000) {
            // If there were many unsuccessfull mutations, try a large mutation
            gen_vector(n->num_coeffs, random_double(0, 1), n->coeffs_delta);
        } else {
            gen_vector(n->num_coeffs, random_double(0, n->mutation_step), n->coeffs_delta);
        }
    }
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        n->coeffs[i] = control_coeffs_func(n->coeffs[i] + n->coeffs_delta[i]);
    }
    n->mutated = 1;
}

// The opposite is neuron_stash_state
void neuron_rollback(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        n->coeffs[i] = n->coeffs_backup[i];
    }
    if(n->mutated == 1) {
        n->bad_mutations_counter ++;
        n-> mutated = 0;
    }
}
