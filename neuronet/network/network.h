#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "network_types.h"

void network_create(uint32_t data[]);
double *network_get_outputs(double *inputs);
void network_mutate(void);
void network_rollback(void);

// Helper functions:
network_t *unpack_network_description(uint32_t data[]);
