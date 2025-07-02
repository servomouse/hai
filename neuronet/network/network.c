#include "network.h"
#include "neuron.h"
#include "mymath.h"

network_t *network;

void network_create(uint32_t data[]) {
    network = unpack_network_description(data);
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

void network_mutate(void) {
    network->mutated_neuron_idx = random_int(0, network->num_neurons);
    neuron_mutate(&network->neurons[network->mutated_neuron_idx]);
}

void network_rollback(void) {
    neuron_rollback(&network->neurons[network->mutated_neuron_idx]);
}

net_coeffs_t * network_get_coeffs(void) {
    net_coeffs_t *result = (net_coeffs_t*)calloc(1, sizeof(net_coeffs_t));
    result->items = (char**)calloc(network->num_neurons, sizeof(char*));
    result->num_items = network->num_neurons;
    for(uint32_t i=0; i<network->num_neurons; i++) {
        result->items[i] = neuron_get_coeffs(&network->neurons[i]);
    }
    return result;
}
