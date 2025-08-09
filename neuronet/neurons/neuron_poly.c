#include "neuron.h"

void neuron_poly_create(neuron_t *n, uint32_t num_inputs) {
    if(num_inputs > 8) {
        RAISE("Error: Trying ot create a poly neuron with %d inputs. Max allowed num_inputs is 8!\n", num_inputs);
    }
    n->type = Poly;
    n->num_inputs = num_inputs;
    n->num_coeffs = 1 << num_inputs;
    n->inputs = (double*)calloc(n->num_inputs, sizeof(double));
    n->input_indices = (uint32_t*)calloc(n->num_inputs, sizeof(uint32_t));
    n->coeffs = calloc(n->num_coeffs, sizeof(double));
    n->coeffs_backup = calloc(n->num_coeffs, sizeof(double));
    n->coeffs_delta = calloc(n->num_coeffs, sizeof(double));
    n->bp_deltas = calloc(n->num_coeffs, sizeof(backprop_error_t));
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = random_double(-0.1, 0.1);
    }
}

double neuron_poly_get_output(neuron_t *n, double *inputs) {
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->inputs[i] = inputs[n->input_indices[i]];
    }
    n->weighted_sum = ((double*)n->coeffs)[0]; // BIAS
    for(uint32_t i=1; i<n->num_coeffs; i++) {
        for(uint32_t j=0; j<n->num_inputs; j++) {
            if(((1 << j) & i) > 0) {
                n->weighted_sum += n->inputs[i] * ((double*)n->coeffs)[j];
            }
        }
    }
    n->output = activation_func(n->weighted_sum);
    return n->output;
}

char *neuron_poly_get_coeffs(neuron_t *n) {
    char *coeffs = doubles_to_string(n->coeffs, n->num_coeffs);
    return coeffs;
}

void neuron_poly_set_coeffs(neuron_t *n, double *values) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = values[i];
    }
}

/* MUTATIONS */

// The opposite is neuron_rollback
void neuron_poly_stash_state(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs_backup)[i] = ((double*)n->coeffs)[i];
    }
}

void neuron_poly_mutate(neuron_t * n, double mutation_step) {
    neuron_poly_stash_state(n);
    gen_vector(n->num_coeffs, random_double(0, mutation_step), (double*)n->coeffs_delta);
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = control_coeffs_func(
            ((double*)n->coeffs)[i] + ((double*)n->coeffs_delta)[i]
        );
    }
}

// The opposite is neuron_stash_state
void neuron_poly_rollback(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = ((double*)n->coeffs_backup)[i];
    }
}

/* BACKPROPAGATION */

void neuron_poly_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    double derivative = 1.0 - pow(tanh(n->weighted_sum), 2);
    if(0 == errors[self_idx].counter) {
        printf("Neuron %d suspicious error: backpropagation error"
            " counter is 0. Is the neuron connected to anything?", self_idx);
    }
    double output_error = (errors[self_idx].error_sum / errors[self_idx].counter) * derivative;
    errors[self_idx].error_sum = 0;
    errors[self_idx].counter = 0;

    n->bp_deltas[0].error_sum += output_error;
    n->bp_deltas[0].counter++;

    for (uint32_t i = 1; i < n->num_coeffs; i++) {
        double input_product = 1.0;
        for (uint32_t j = 0; j < n->num_inputs; j++) {
            if ((i >> j) & 1) {
                input_product *= n->inputs[j];
            }
        }
        n->bp_deltas[i].error_sum += output_error * input_product;
        n->bp_deltas[i].counter++;
    }
    for (uint32_t j = 0; j < n->num_inputs; j++) {
        double input_error = 0.0;
        for (uint32_t i = 1; i < n->num_coeffs; i++) {
            if ((i >> j) & 1) {
                double other_inputs_product = 1.0;
                for (uint32_t k = 0; k < n->num_inputs; k++) {
                    if (k != j && ((i >> k) & 1)) {
                        other_inputs_product *= n->inputs[k];
                    }
                }
                input_error += output_error * ((double*)n->coeffs)[i] * other_inputs_product;
            }
        }
        errors[n->input_indices[j]].error_sum += input_error;
        errors[n->input_indices[j]].counter++;
    }
}

void neuron_poly_backprop_update_weights(neuron_t *n, double learning_rate) {
    for (uint32_t i = 0; i < n->num_coeffs; i++) {
        if (n->bp_deltas[i].counter == 0) {
            n->bp_deltas[i].error_sum = 0;
            continue;
        }
        double delta = n->bp_deltas[i].error_sum / n->bp_deltas[i].counter;
        ((double*)n->coeffs)[i] = control_coeffs_func(
            ((double*)n->coeffs)[i] + (learning_rate * delta)
        );
        n->bp_deltas[i].error_sum = 0;
        n->bp_deltas[i].counter = 0;
    }
}
