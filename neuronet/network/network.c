#include "network.h"
#include "neuron.h"
#include "mymath.h"
#include "utils.h"
#include <time.h>

network_t *network;

/* Network is represented as a 1d array of neurons, first neurons are expected to be inputs, the last neurons are outputs */
DLL_PREFIX
void network_create(uint32_t net_arch[]) {
    network = unpack_network_description(net_arch);
}

DLL_PREFIX
double * network_get_outputs(double *inputs) {
    for(uint32_t i=0; i<network->size; i++) {
        if(i < network->num_inputs) {
            network->arr[i] = inputs[i];
        } else {
            network->arr[i] = neuron_get_output(&network->neurons[i-network->num_inputs], network->arr);
        }
    }
    for(uint32_t i=0; i<network->num_outputs; i++) {
        uint32_t idx = network->output_indices[i];
        network->outputs[i] = network->arr[idx];
    }
    return network->outputs;
}

DLL_PREFIX
void network_mutate(double mutation_step) {
    network->mutated_neuron_idx = random_int(0, network->num_neurons);
    neuron_mutate(&network->neurons[network->mutated_neuron_idx], mutation_step);
}

DLL_PREFIX
void network_rollback(void) {
    neuron_rollback(&network->neurons[network->mutated_neuron_idx]);
}
DLL_PREFIX
char * network_get_coeffs(uint32_t idx) {
    if(idx >= network->num_neurons)
        RAISE("Error: idx is outside of the array: idx = %d, num_neurons: %d\n", idx, network->num_neurons);
    return neuron_get_coeffs(&network->neurons[idx]);
}

DLL_PREFIX
void network_set_coeffs(uint32_t idx, double *values) {
    if(idx >= network->num_neurons)
        RAISE("Error: idx is outside of the array: idx = %d, num_neurons: %d\n", idx, network->num_neurons);
    // printf("Setting coeffs for the neuron %d\n", idx);
    neuron_set_coeffs(&network->neurons[idx], values);
}

DLL_PREFIX
void network_free(void *ptr) {
    if(ptr != NULL) {
        free(ptr);
    }
}

DLL_PREFIX
void network_init_rng(size_t seed) {
    srand(seed);
}

DLL_PREFIX
void network_backpropagation(double *errors) {
    for(uint32_t i=0; i<network->num_outputs; i++) {    // Set initial errors
        uint32_t idx = network->output_indices[i];
        network->bp_errors[idx].error_sum += errors[i];
        network->bp_errors[idx].counter ++;
    }
    for(uint32_t i=network->size-1; i>=network->num_inputs; i--) {  // network[:num_inputs] aren't real neurons, so skip them
        neuron_backpropagate(&network->neurons[i-network->num_inputs], network->bp_errors, i);
    }
}

DLL_PREFIX
void network_backprop_update_weights(double learning_rate) {
    for(uint32_t i=0; i<network->num_neurons; i++) {
        neuron_backprop_update_weights(&network->neurons[i], learning_rate);
    }
    for(uint32_t i=0; i<network->num_inputs; i++) { // Null-out pseudo-neurons to keep the system clean
        network->bp_errors[i].error_sum = 0;
        network->bp_errors[i].counter = 0;
    }
}
