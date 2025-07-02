#include "network.h"

uint32_t net_maps[] = {
    // Network_config:
    0,  // Num micronets
    40, // Main net description size
    4,  // Net num inputs
    8,  // Net size
    4,  // Net num outputs
    4,  // Net output indices:
    5,
    6,
    7,
    // Neurons:
    //  Size    idx num_inputs  type    indices:
        8,      4,  4,          0,      0, 1, 2, 3,
        8,      5,  4,          0,      0, 1, 2, 3,
        8,      6,  4,          0,      0, 1, 2, 3,
        8,      7,  4,          0,      0, 1, 2, 3,
};

int main(void) {
    network_create(net_maps);
    double inputs[] = {1, 1, 1, 1};
    double *outputs = network_get_outputs(inputs);
    printf("Outputs: [%f, %f, %f, %f]\n", outputs[0], outputs[1], outputs[2], outputs[3]);
    return EXIT_SUCCESS;
}