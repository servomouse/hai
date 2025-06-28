#include "neuron.h"

void neuron_linear_create(neuron_t *n, uint32_t num_inputs) {
    n->type = Linear;
    n->num_inputs = num_inputs;
    n->num_coeffs = num_inputs+1;
    n->inputs = (double*)calloc(n->num_inputs, sizeof(double));
    n->input_indices = (double*)calloc(n->num_inputs, sizeof(uint32_t));
    n->coeffs = (double*)calloc(n->num_coeffs, sizeof(double));
    n->coeffs_backup = (double*)calloc(n->num_coeffs, sizeof(double));
    n->coeffs_delta = (double*)calloc(n->num_coeffs, sizeof(double));
    n->mutation_step = 0.001;
}

double neuron_linear_get_output(neuron_t *n) {
    n->output = n->coeffs[n->num_coeffs-1]; // BIAS
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->output += n->inputs[i] * n->coeffs[i];
    }
    n->output = activation_func(n->output);
    return n->output;
}
