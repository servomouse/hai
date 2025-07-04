#include "network.h"
#include "neuron.h"
#include "mymath.h"
#include "utils.h"

network_t *network;

void network_create(uint32_t net_arch[]) {
    network = unpack_network_description(net_arch);
}

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

void network_mutate(double mutation_step) {
    network->mutated_neuron_idx = random_int(0, network->num_neurons);
    neuron_mutate(&network->neurons[network->mutated_neuron_idx], mutation_step);
}

void network_rollback(void) {
    neuron_rollback(&network->neurons[network->mutated_neuron_idx]);
}

char * network_get_coeffs(uint32_t idx) {
    if(idx >= network->num_neurons)
        RAISE("Error: idx is outside of the array: idx = %d, num_neurons: %d\n", idx, network->num_neurons);
    return neuron_get_coeffs(&network->neurons[idx]);
}

void network_set_coeffs(uint32_t idx, double *values) {
    if(idx >= network->num_neurons)
        RAISE("Error: idx is outside of the array: idx = %d, num_neurons: %d\n", idx, network->num_neurons);
    printf("Setting coeffs for the neuron %d\n", idx);
    neuron_set_coeffs(&network->neurons[idx], values);
}
