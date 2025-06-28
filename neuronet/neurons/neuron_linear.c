#include "neuron.h"

void neuron_linear_create(neuron_t *n, uint32_t num_inputs) {
    n->type = Linear;
    n->num_inputs = num_inputs;
    n->num_coeffs = num_inputs+1;
    n->inputs = (double*)calloc(n->num_inputs, sizeof(double));
    n->coeffs = (double*)calloc(n->num_coeffs, sizeof(double));
}

double neuron_linear_get_output(neuron_t *n) {
    n->output = n->coeffs[n->num_coeffs-1]; // BIAS
    for(uint32_t i=0; i<n->num_inputs; i++) {
        n->output += n->inputs[i] * n->coeffs[i];
    }
    n->output = activation_func(n->output);
    return n->output;
}
