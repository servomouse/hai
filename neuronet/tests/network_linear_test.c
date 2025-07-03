#include "network.h"
#include <time.h>

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

double get_error(uint32_t num_values, double *result, double *target) {
    double error = 0;
    for(uint32_t i=0; i<num_values; i++) {
        error += (target[i] - result[i]) * (target[i] - result[i]);
    }
    error /= num_values;
    return error;
}

uint32_t test_evolution(void) {
    // uint32_t seed = time(NULL);
    uint32_t seed = 1751501246;
    // printf("Seed: %d\n", seed);
    srand(seed);
    network_create(net_maps);
    double inputs[] = {0.2, -0.2, 0.2, -0.2};
    double expected_outputs[] = {0.1, -0.3, 0.5, -0.7};
    double *outputs = network_get_outputs(inputs);

    printf("Outputs: [%f, %f, %f, %f]\n", outputs[0], outputs[1], outputs[2], outputs[3]);
    net_coeffs_t *coeffs = network_get_coeffs();
    printf("Network coeffs:\n");
    for(uint32_t i=0; i<coeffs->num_items; i++) {
        printf("%d: %s\n", i, coeffs->items[i]);
        free(coeffs->items[i]);
    }
    free(coeffs);

    double error = get_error(4, outputs, expected_outputs);
    printf("Initial error: %f\n", error);
    uint32_t counter = 0;
    while((error > 0.001) && counter++ < 1000) {
        network_mutate(0.1);
        outputs = network_get_outputs(inputs);
        double new_error = get_error(4, outputs, expected_outputs);
        if(new_error > error) {
            network_rollback();
        } else if(new_error < error) {
            error = new_error;
            // printf("New error: %f\n", new_error);
        }
    }
    printf("Final error: %f, counter = %d\n", error, counter);

    outputs = network_get_outputs(inputs);
    printf("Outputs: [%f, %f, %f, %f]\n", outputs[0], outputs[1], outputs[2], outputs[3]);
    coeffs = network_get_coeffs();
    printf("Network coeffs:\n");
    for(uint32_t i=0; i<coeffs->num_items; i++) {
        printf("%d: %s\n", i, coeffs->items[i]);
        free(coeffs->items[i]);
    }
    free(coeffs);
    if(counter == 124) {
        return EXIT_SUCCESS;
    }
    return EXIT_FAILURE;
}

int main(void) {

    return test_evolution();
}