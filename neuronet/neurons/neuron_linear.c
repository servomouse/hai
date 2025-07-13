#include "neuron.h"
#include "mymath.h"

void neuron_linear_create(neuron_t *n, uint32_t num_inputs) {
    n->type = Linear;
    n->num_inputs = num_inputs;
    n->num_coeffs = num_inputs+1;
    n->inputs = (double*)calloc(n->num_inputs, sizeof(double));
    n->input_indices = (uint32_t*)calloc(n->num_inputs, sizeof(uint32_t));
    n->coeffs = calloc(n->num_coeffs, sizeof(double));
    n->coeffs_backup = calloc(n->num_coeffs, sizeof(double));
    n->coeffs_delta = calloc(n->num_coeffs, sizeof(double));
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = random_double(-1.0, 1.0);
    }
}

double neuron_linear_get_output(neuron_t *n) {
    n->weighted_sum = ((double*)n->coeffs)[n->num_coeffs-1]; // BIAS
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->weighted_sum += n->inputs[i] * ((double*)n->coeffs)[i];
    }
    n->output = activation_func(n->weighted_sum);
    return n->output;
}

char *neuron_linear_get_coeffs(neuron_t *n) {
    char *coeffs = doubles_to_string((double*)n->coeffs, n->num_coeffs);
    return coeffs;
}

void neuron_linear_set_coeffs(neuron_t *n, double *values) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = values[i];
    }
}

/* MUTATIONS */

// The opposite is neuron_rollback
void neuron_linear_stash_state(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs_backup)[i] = ((double*)n->coeffs)[i];
    }
}

void neuron_linear_mutate(neuron_t * n, double mutation_step) {
    neuron_linear_stash_state(n);
    gen_vector(n->num_coeffs, random_double(0, mutation_step), (double*)n->coeffs_delta);
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = control_coeffs_func(((double*)n->coeffs)[i] + ((double*)n->coeffs_delta)[i]);
    }
}

// The opposite is neuron_stash_state
void neuron_linear_rollback(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = ((double*)n->coeffs_backup)[i];
    }
}

/* BACKPROPAGATION */

void neuron_linear_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    double learning_rate = 0.01;
    double derivative = 1.0 - pow(tanh(n->weighted_sum), 2);  // Derivative of the activation function
    double output_error = (errors[self_idx].error_sum / errors[self_idx].counter) * derivative;
    errors[self_idx].error_sum = 0;
    errors[self_idx].counter = 0;

    for (uint32_t i = 0; i < n->num_inputs; i++) {
        errors[n->input_indices[i]].error_sum = output_error * ((double*)n->coeffs)[i];
        errors[n->input_indices[i]].counter ++;

        double delta = output_error * n->inputs[i];
        ((double*)n->coeffs)[i] += learning_rate * delta;
    }
    double bias_delta = output_error; // Update the bias
    ((double*)n->coeffs)[n->num_coeffs - 1] += learning_rate * bias_delta;
}
