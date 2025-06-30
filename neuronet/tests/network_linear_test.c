#include "network.h"

uint32_t main_net_neurons[] = {
    4, 4, Linear, 0, 0, 1, 2, 3,
    5, 4, Linear, 1, 0, 1, 2, 3,
    6, 4, Linear, 2, 0, 1, 2, 3,
    7, 4, Linear, 3, 0, 1, 2, 3,
};

network_map_t main_net_map = {
    .num_inputs = 4,
    .net_size = 8,
    .num_outputs = 4,
    .neurons = (neuron_description_t*)&main_net_neurons
};

int main(void) {
    network_create(&main_net_map, NULL);
    double inputs[] = {1, 1, 1, 1};
    double *outputs = network_get_outputs(inputs);
    printf("Outputs: [%f, %f, %f, %f]\n", outputs[0], outputs[1], outputs[2], outputs[3]);
    return EXIT_SUCCESS;
}