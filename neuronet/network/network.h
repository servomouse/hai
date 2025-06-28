#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "network_types.h"

// Interface:

void network_create(network_type_t *net, network_map_t *map);
void network_get_outputs(network_type_t *net, double *inputs, double *otputs);
