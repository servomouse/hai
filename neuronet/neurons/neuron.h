#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include "neuron_types.h"

void neuron_create(neuron_t *n, neuron_description_t *info);
// void neuron_set_coeff(neuron_t *n, uint32_t idx, double value);     // Set specific coefficient
void neuron_set_coeffs(neuron_t *n, double *values);                // Set all coefficients
char * neuron_get_coeffs(neuron_t *n);                  // Returns coefficients as a string, free after use
// double neuron_get_coeff(neuron_t *n, uint32_t idx);     // Get the value of a specific coefficient
double neuron_get_output(neuron_t *n, double *inputs);
double activation_func(double value);

// The mutations feature:
double control_coeffs_func(double coeff);
void neuron_stash_state(neuron_t * n);  // The opposite is neuron_rollback
void neuron_mutate(neuron_t * n, double mutation_step);
void neuron_rollback(neuron_t * n);     // The opposite is neuron_stash_state
