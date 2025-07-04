#include <time.h>
#include "network.h"
#include "utils.h"
#include "mymath.h"

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

void test_evolution(void) {
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
    if(counter != 124) {
        RAISE("Error: counter value (%d) isn't correct!\n", counter);
    }
}

void test_coeffs_set_get(void) {
    double init_coeffs[4][5] = {
        {-0.284830, -0.363750, -0.479110, 0.422350, 0.555100},
        {-0.862970, 0.976810, 0.121800, -0.568650, 0.056610},
        {-0.844970, 0.030000, 0.616080, -0.939820, 0.615710},
        {-0.199870, 0.150060, 0.022310, 0.744130, -0.750420}
    };
    double final_coeffs[4][5] = {
        {-0.371300, -0.438380, -0.519600, 0.444090, 0.280620},
        {-0.957770, 0.977300, 0.133530, -0.596600, -0.059860},
        {-0.817640, -0.108050, 0.704190, -0.780050, 0.341150},
        {-0.171120, 0.210090, 0.009990, 0.852520, -0.512110}
    };
    double init_error = 0.058516;
    double final_error = 0.000813;
    double inputs[] = {0.2, -0.2, 0.2, -0.2};
    double expected_outputs[] = {0.1, -0.3, 0.5, -0.7};

    // Test with initial coefficients
    for(uint32_t i=0; i<4; i++) {
        double *coeffs = init_coeffs[i];
        network_set_coeffs(i, coeffs);
    }
    double *outputs = network_get_outputs(inputs);
    double error = get_error(4, outputs, expected_outputs);
    // printf("Init error: %f, expected value: %f, are_equal: %d\n", error, init_error, are_equal(error, init_error, 6));
    if(!are_equal(error, init_error, 6)) {
        RAISE("Error: init error value (%f) isn't correct!\n", error);
    }

    // Test with final coefficients
    for(uint32_t i=0; i<4; i++) {
        network_set_coeffs(i, final_coeffs[i]);
    }
    outputs = network_get_outputs(inputs);
    error = get_error(4, outputs, expected_outputs);
    // printf("Final error: %f, expected value: %f, are_equal: %d\n", error, final_error, are_equal(error, final_error, 6));
    if(!are_equal(error, final_error, 6)) {
        RAISE("Error: init error value (%f) isn't correct!\n", error);
    }
}

int main(void) {
    // uint32_t seed = time(NULL);
    // printf("Seed: %d\n", seed);
    uint32_t seed = 1751501246;
    srand(seed);
    network_create(net_maps);
    test_evolution();
    test_coeffs_set_get();
    return EXIT_SUCCESS;
}