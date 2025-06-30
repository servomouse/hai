#include "network.h"
#include "neuron.h"

network_t *network;

static void _create(network_t *net, network_map_t *map, uint8_t is_micronet) {
    net->is_micronet = is_micronet;
    net->num_inputs = map->num_inputs;
    net->num_neurons = map->net_size - map->num_inputs;
    net->num_outputs = map->num_outputs;
    net->size = map->net_size;
    net->mutated_neuron_idx = 0;

    net->arr = (double*)calloc(net->size, sizeof(double));
    net->outputs = (double*)calloc(net->num_outputs, sizeof(double));
    net->output_indices = (uint32_t*)calloc(net->num_outputs, sizeof(uint32_t));
    net->neurons = (neuron_t*)calloc(net->num_neurons, sizeof(neuron_t));

    // Initialize neurons:
    uint32_t *neurons = (uint32_t*)map->neurons;
    uint32_t offset = 0;
    for(uint32_t i=0; i<net->num_neurons; i++) {
        neuron_description_t *neuron = (neuron_description_t *)&neurons[offset];
        neuron_create(&net->neurons[i], neuron);
        net->output_indices[neuron->output_idx] = i;
    }
    // TODO: Add copy_maps
}

void network_create(network_map_t *net_map, network_map_t *micronet_maps) {
    network = calloc(1, sizeof(network_t));
    _create(network, net_map, 0);
    if(micronet_maps) {
        network->micronets = calloc(Neuron_types_num, sizeof(network_t));
        for(uint32_t i=0; i<Neuron_types_num; i++) {
            _create(&network->micronets[i], &micronet_maps[i], 1);
        }
    }
}

double * network_get_outputs(double *inputs) {
    for(uint32_t i=0; i<network->size; i++) {
        if(i < network->num_inputs) {
            network->arr[i] = inputs[i];
        } else {
            network->arr[i] = neuron_get_output(&network->neurons[i], network->arr);
        }
    }
    for(uint32_t i=0; i<network->num_outputs; i++) {
        uint32_t idx = network->output_indices[i];
        network->outputs[i] = network->arr[idx];
    }
    return network->outputs;
}