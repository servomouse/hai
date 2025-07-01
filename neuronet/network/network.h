#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "network_types.h"

void network_create(network_map_t *net_map, network_map_t *micronet_maps);   // Provide all the micronet maps or NULL
double *network_get_outputs(double *inputs);
void network_mutate(void);
void network_rollback(void);
