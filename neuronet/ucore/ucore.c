#include "ucore.h"
#include "neuron.h"

#define LAYER_SIZE 16
#define LATERAL_LAYER_NUM_LINKS 8
#define LATERAL_LAYER_NUM_INPUTS ((LATERAL_LAYER_NUM_LINKS + 2) * LAYER_SIZE)

// Layers:
#define INPUT_LAYER_OFFSET    0                                     // Input layer
#define LATERAL_LAYER_OFFSET  (INPUT_LAYER_OFFSET + LAYER_SIZE)     // CU lateral
#define HIDDEN_0_LAYER_OFFSET (LATERAL_LAYER_OFFSET + LAYER_SIZE)   // CU hidden
#define HIDDEN_1_LAYER_OFFSET (HIDDEN_0_LAYER_OFFSET + LAYER_SIZE)  // CU hidden
#define HIDDEN_2_LAYER_OFFSET (HIDDEN_1_LAYER_OFFSET + LAYER_SIZE)  // CU hidden
#define OUTPUT_LAYER_OFFSET   (HIDDEN_2_LAYER_OFFSET + LAYER_SIZE)  // Outputs

#define NUM_NEURONS (OUTPUT_LAYER_OFFSET + LAYER_SIZE)

ucore_t * create_ucore(uint32_t num_inputs, uint32_t num_lateral_links) {
    ucore_t *ucore = (ucore_t*)calloc(1, sizeof(ucore_t));
    ucore->num_inputs = num_inputs;
    ucore->lateral_num_links = num_lateral_links;
    ucore->lateral_num_inputs = ((ucore->lateral_num_links + 2) * LAYER_SIZE);
    ucore->arr =             (double*)calloc(NUM_NEURONS, sizeof(double));
    ucore->neurons =         (neuron_t*)calloc(NUM_NEURONS, sizeof(neuron_t));
    ucore->core_inputs =     (double*)calloc(ucore->num_inputs, sizeof(double));
    ucore->lateral_inputs =  (double*)calloc(ucore->lateral_num_inputs, sizeof(double));
    ucore->lateral_outputs = (double*)calloc(LAYER_SIZE, sizeof(double));
    ucore->core_outputs =    (double*)calloc(LAYER_SIZE, sizeof(double));

    // Create input layer:
    for(uint32_t i=0; i<LAYER_SIZE; i++) {
        neuron_create_simple(&ucore->neurons[i], Linear, ucore->num_inputs);
        for(uint32_t j=0; j<ucore->num_inputs; j++) {
            neuron_map_input(&ucore->neurons[i], j, j);
        }
    }
    // Create lateral layer:
    for(uint32_t i=LATERAL_LAYER_OFFSET; i<HIDDEN_0_LAYER_OFFSET; i++) {
        neuron_create_simple(&ucore->neurons[i], Linear, ucore->lateral_num_inputs);
        for(uint32_t j=0; j<ucore->lateral_num_inputs; j++) {
            neuron_map_input(&ucore->neurons[i], j, j);
        }
    }
    // Create other layers:
    for(uint32_t i=0; i<LAYER_SIZE; i++) {
        neuron_create_simple(&ucore->neurons[i+HIDDEN_0_LAYER_OFFSET], Linear, LAYER_SIZE);
        neuron_create_simple(&ucore->neurons[i+HIDDEN_1_LAYER_OFFSET], Linear, LAYER_SIZE);
        neuron_create_simple(&ucore->neurons[i+HIDDEN_2_LAYER_OFFSET], Linear, LAYER_SIZE);
        neuron_create_simple(&ucore->neurons[i+OUTPUT_LAYER_OFFSET],   Linear, LAYER_SIZE);
        for(uint32_t j=0; j<LAYER_SIZE; j++) {
            neuron_map_input(&ucore->neurons[i+HIDDEN_0_LAYER_OFFSET], j, j+LATERAL_LAYER_OFFSET);
            neuron_map_input(&ucore->neurons[i+HIDDEN_1_LAYER_OFFSET], j, j+HIDDEN_0_LAYER_OFFSET);
            neuron_map_input(&ucore->neurons[i+HIDDEN_2_LAYER_OFFSET], j, j+HIDDEN_1_LAYER_OFFSET);
            neuron_map_input(&ucore->neurons[i+OUTPUT_LAYER_OFFSET],   j, j+HIDDEN_2_LAYER_OFFSET);
        }
    }
    return ucore;
}

void core_process_inputs(ucore_t *c, double *inputs) {
    for(uint32_t i=0; i<c->num_inputs; i++) {
        c->core_inputs[i] = inputs[i];
    }
    for(uint32_t i=0; i<LAYER_SIZE; i++) {
        c->arr[i] = neuron_get_output(&c->neurons[i], inputs);
    }
}

// Lateral layer inputs map:
// [0:LAYER_SIZE] - the same layer outputs
// [LAYER_SIZE:LAYER_SIZE*9] - outputs of the neighboring ucore's lateral layers
// [LAYER_SIZE*9:ucore->lateral_num_inputs] - outputs of the input layer of the same ucore
double * core_prepare_lateral_layer(ucore_t *c) {
    for(uint32_t i=0; i<c->lateral_num_inputs; i++) {
        if(i < (c->lateral_num_inputs - LAYER_SIZE)) {
            c->lateral_inputs[i] = 0;
        } else {
            c->lateral_inputs[i] = c->arr[i];
        }
    }
    for(uint32_t i=0; i<LAYER_SIZE; i++) {
        double temp = neuron_get_output(&c->neurons[LAYER_SIZE+i], c->lateral_inputs);
        c->arr[LAYER_SIZE+i] = temp;
        c->lateral_outputs[i] = temp;
    }
    return c->lateral_outputs;
}

double * core_update_lateral_layer(ucore_t *c, double *inputs) {
    for(uint32_t i=0; i<c->lateral_num_inputs; i++) {
        if(i < LAYER_SIZE*9) {
            c->lateral_inputs[i] = 0;
        } else {
            c->lateral_inputs[i] = c->arr[i];
        }
    }
    for(uint32_t i=0; i<LAYER_SIZE; i++) {
        double temp = neuron_get_output(&c->neurons[LAYER_SIZE+i], c->lateral_inputs);
        c->arr[LAYER_SIZE+i] = temp;
        c->lateral_outputs[i] = temp;
    }
    return c->lateral_outputs;
}

double * core_get_outputs(ucore_t *c) {
    for(uint32_t i=HIDDEN_0_LAYER_OFFSET; i<NUM_NEURONS; i++) {
        double temp = neuron_get_output(&c->neurons[i], c->arr);
        c->arr[i] = temp;
        if(i >= OUTPUT_LAYER_OFFSET) {
            c->core_outputs[i-OUTPUT_LAYER_OFFSET] = temp;
        }
    }
    return c->core_outputs;
}
