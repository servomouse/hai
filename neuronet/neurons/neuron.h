#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "neuron_types.h"

// Interface:

void create_neuron(neuron_t *n, neuron_type_t type, uint32_t num_inputs);
void neuron_set_coeff(neuron_t *n, uint32_t idx, double value);     // Set specific coefficient
void neuron_set_coeffs(neuron_t *n, double *values);                // Set all coefficients
double * neuron_get_coeffs(neuron_t *n);                // Returns a pointer to an array of all coefficients, free after use
double neuron_get_coeff(neuron_t *n, uint32_t idx);     // Get the value of a specific coefficient
double neuron_get_output(neuron_t *n, double *inputs);
