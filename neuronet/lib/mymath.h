#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

typedef struct {
    double real;
    double imag;
} complex_value_t;

/* Returns a random double number within the range min to max */
double random_double(double min, double max);

// Returns a random integer, min values is min, max value is max-1
uint32_t random_int(uint32_t min, uint32_t max);

uint8_t random_bit(void);   // Returns 0 or 1 randomly

uint8_t count_bits(size_t value);

// Generates a random vector of given length in an n-dimensional space
void gen_vector(uint32_t n, double len, double* result);

double complex_vector_length(uint32_t n, complex_value_t* vector);

// Generates a random 2d vector (a complex vector) of given length in an n-dimensional space
complex_value_t * gen_complex_vector(uint32_t n, double len);

// Precision is how many digits after the decimal point
double round_to_precision(double value, uint32_t precision);

int are_equal(double val1, double val2, int precision);

uint64_t get_hash(uint8_t *data, size_t size);
