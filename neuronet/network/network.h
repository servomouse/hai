#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "network_types.h"

void network_create(uint32_t data[]);
double *network_get_outputs(double *inputs);
void network_mutate(double mutation_step);  // mutation_step is a vector length between 0 and 1
void network_rollback(void);
net_coeffs_t * network_get_coeffs(void);
void network_set_coeffs(uint32_t idx, double *values);

// Helper functions:
network_t *unpack_network_description(uint32_t data[]);
