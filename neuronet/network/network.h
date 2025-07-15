#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "network_types.h"

void network_create(uint32_t net_arch[]);
double *network_get_outputs(double *inputs);
void network_mutate(double mutation_step);  // mutation_step is a value between 0 and 1
void network_rollback(void);
void network_backpropagation(double *errors);
void network_backprop_update_weights(double learning_rate);

// Returns a list of coeffs of a given neuron as a string like this: {-0.123457, 0.987654, -0.456789}. Free after use
char * network_get_coeffs(uint32_t idx);
void network_set_coeffs(uint32_t idx, double *values);
void network_free(void *ptr);   // Provides the ability to free allocated memory from outside of the SO/DLL
void network_init_rng(size_t seed); // Init RNG with a seed (for repeatability in tests)

// Helper functions:
network_t *unpack_network_description(uint32_t data[]);
