#include "neuron.h"
#include "utils.h"
#include "neuron_linear.c"
#include "neuron_poly.c"
#include "neuron_pattern.c"

void neuron_create(neuron_t *n, neuron_type_t n_type, uint32_t num_inputs) {
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
        default:
            RAISE("Error: Unknown neuron type: %d\n", n_type);
    }
}

void neuron_set_coeff(neuron_t *n, uint32_t idx, double value) {
    ;
}

void neuron_set_coeffs(neuron_t *n, double *values) {
    ;
}

double * neuron_get_coeffs(neuron_t *n) {
    return 0;
}

double neuron_get_coeff(neuron_t *n, uint32_t idx) {
    return 0;
}

double neuron_get_output(neuron_t *n, double *inputs) {
    // TODO: Process inputs
    switch(n->type) {
        case Linear:
            return neuron_linear_get_output(n);
        case Poly:
            return neuron_poly_get_output(n);
        case Pattern:
            return neuron_pattern_get_output(n);
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
