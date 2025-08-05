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
    n->bp_deltas = calloc(n->num_coeffs, sizeof(backprop_error_t));
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = random_double(-0.1, 0.1);
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
        ((double*)n->coeffs)[i] = control_coeffs_func(
            ((double*)n->coeffs)[i] + ((double*)n->coeffs_delta)[i]
        );
    }
}

// The opposite is neuron_stash_state
void neuron_linear_rollback(neuron_t * n) {
    for(uint32_t i=0; i<n->num_coeffs; i++) {
        ((double*)n->coeffs)[i] = ((double*)n->coeffs_backup)[i];
    }
}

/* BACKPROPAGATION */

void neuron_linear_backpropagate_new(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    if(0 == errors[self_idx].counter) {
        printf("Neuron %d suspicious error: backpropagation error"
            " counter is 0. Is neuron connected to anything?", self_idx);
    }
    double error = errors[self_idx].error_sum / errors[self_idx].counter;
    errors[self_idx].error_sum = 0;
    errors[self_idx].counter = 0;

    for (uint32_t i = 0; i < n->num_inputs; i++) {
        double coeff = ((double*)n->coeffs)[i];
        double input = n->inputs[i];
        double delta = 0;
        if(error > 0) { // Output is too high
            if((input > 0) && (coeff > 0)) {
                delta -= random_double(0.5, 1.0);   // -: move down, +: move up
            } else if((input > 0) && (coeff < 0)) {
                delta -= random_double(0.5, 1.0);   // -: move down, +: move up
            } else if((input < 0) && (coeff > 0)) {
                delta += random_double(0.5, 1.0);   // -: move up, +: move down
            } else {    // (input < 0) && (coeff < 0)
                delta += random_double(0.5, 1.0);   // -: move up, +: move down
            }
        } else if(error < 0) {  // Output is too low
            if((input > 0) && (coeff > 0)) {
                delta += random_double(0.5, 1.0);   // -: move down, +: move up
            } else if((input > 0) && (coeff < 0)) {
                delta += random_double(0.5, 1.0);   // -: move down, +: move up
            } else if((input < 0) && (coeff > 0)) {
                delta -= random_double(0.5, 1.0);   // -: move up, +: move down
            } else {    // (input < 0) && (coeff < 0)
                delta -= random_double(0.5, 1.0);   // -: move up, +: move down
            }
        }
        n->bp_deltas[i].error_sum += delta;
        n->bp_deltas[i].counter ++;
    }
    for (uint32_t i = 0; i < n->num_inputs; i++) {
        double coeff = ((double*)n->coeffs)[i];
        double input = n->inputs[i];
        double delta = 0;
        if(error > 0) { // Output is too high
            if((input > 0) && (coeff > 0)) {
                delta += random_double(0.5, 1.0);   // -: move down, +: move up
            } else if((input > 0) && (coeff < 0)) {
                delta -= random_double(0.5, 1.0);   // -: move up, +: move down
            } else if((input < 0) && (coeff > 0)) {
                delta += random_double(0.5, 1.0);   // -: move down, +: move up
            } else {    // (input < 0) && (coeff < 0)
                delta -= random_double(0.5, 1.0);   // -: move up, +: move down
            }
        } else if(error < 0) {  // Output is too low
            if((input > 0) && (coeff > 0)) {
                delta -= random_double(0.5, 1.0);   // -: move down, +: move up
            } else if((input > 0) && (coeff < 0)) {
                delta += random_double(0.5, 1.0);   // -: move up, +: move down
            } else if((input < 0) && (coeff > 0)) {
                delta -= random_double(0.5, 1.0);   // -: move down, +: move up
            } else {    // (input < 0) && (coeff < 0)
                delta += random_double(0.5, 1.0);   // -: move up, +: move down
            }
        }
        errors[n->input_indices[i]].error_sum += delta;
        errors[n->input_indices[i]].counter ++;
    }
    // Update BIAS:
    if(error > 0) { // Output is too high
        n->bp_deltas[n->num_coeffs - 1].error_sum -= random_double(0, 0.1);
    } else if(error < 0) {  // Output is too low
        n->bp_deltas[n->num_coeffs - 1].error_sum += random_double(0, 0.1);
    }
    n->bp_deltas[n->num_coeffs - 1].counter ++;
}

void neuron_linear_backpropagate(neuron_t *n, backprop_error_t *errors, uint32_t self_idx) {
    double derivative = 1.0 - pow(tanh(n->weighted_sum), 2);  // Derivative of the activation function
    if(0 == errors[self_idx].counter) {
        printf("Neuron %d suspicious error: backpropagation error"
            " counter is 0. Is neuron connected to anything?", self_idx);
    }
    double output_error = (errors[self_idx].error_sum / errors[self_idx].counter) * derivative;
    errors[self_idx].error_sum = 0;
    errors[self_idx].counter = 0;

    for (uint32_t i = 0; i < n->num_inputs; i++) {
        errors[n->input_indices[i]].error_sum = output_error * ((double*)n->coeffs)[i];
        errors[n->input_indices[i]].counter ++;

        n->bp_deltas[i].error_sum += output_error * n->inputs[i];
        n->bp_deltas[i].counter ++;
    }
    double bias_delta = output_error; // Update the bias
    n->bp_deltas[n->num_coeffs - 1].error_sum += bias_delta;
    n->bp_deltas[n->num_coeffs - 1].counter ++;
}

void neuron_linear_backprop_update_weights(neuron_t *n, double learning_rate) {
    for (uint32_t i = 0; i < n->num_coeffs; i++) {
        if(n->bp_deltas[i].counter == 0) {
            n->bp_deltas[i].error_sum = 0;
            continue;
        }
        double delta = n->bp_deltas[i].error_sum / n->bp_deltas[i].counter;
        // Keep coeffs within the [-1, 1] range
        ((double*)n->coeffs)[i] = control_coeffs_func(
            ((double*)n->coeffs)[i] + (learning_rate * delta)
        );
        n->bp_deltas[i].error_sum = 0;
        n->bp_deltas[i].counter = 0;
    }
}
