#include "network.h"
#include "neuron.h"

/* Example:
idx     val
0       0   NUM_MICRONETS
            NET_MAP:
        ---------------------------
1       40  NET_DESCRIPTION_SIZE
2       4   NET_NUM_INPUTS
3       8   NET_SIZE
4       4   NET_NUM_OUTPUTS

5       4   NET_OUTPUT_INDICES:
6       5
7       6
8       7
            NET_NEURONS:
        ---------------------------
9       8   NEURON_DESCRIPTION_SIZE
10      4   NEURON_IDX
11      4   NEURON_NUM_INPUTS
12      0   NEURON_TYPE
            NEURON_INDICES:
13      0
14      1
15      2
16      3
        ---------------------------
17      8   NEURON_DESCRIPTION_SIZE
18      5   NEURON_IDX
19      4   NEURON_NUM_INPUTS
20      0   NEURON_TYPE
            NEURON_INDICES:
21      0
22      1
23      2
24      3
        ---------------------------
25      8   NEURON_DESCRIPTION_SIZE
26      6   NEURON_IDX
27      4   NEURON_NUM_INPUTS
28      0   NEURON_TYPE
            NEURON_INDICES:
29      0
30      1
31      2
32      3
        ---------------------------
33      8   NEURON_DESCRIPTION_SIZE
34      7   NEURON_IDX
35      4   NEURON_NUM_INPUTS
36      0   NEURON_TYPE
            NEURON_INDICES:
37      0
38      1
39      2
40      3
        ---------------------------
*/

// Network description structure:

// For i in range(1 + data[NUM_MICRONETS])
#define NET_DESCRIPTION_SIZE    0
#define NET_NUM_INPUTS          1
#define NET_SIZE                2
#define NET_NUM_OUTPUTS         3
#define NET_OUTPUT_INDICES      4
#define NET_NEURONS             4 // Plus data[NET_NUM_OUTPUTS]
    // For j in range(data[NET_SIZE] - data[NET_NUM_INPUTS])
    #define NEURON_DESCRIPTION_SIZE 0
    #define NEURON_IDX              1
    #define NEURON_NUM_INPUTS       2
    #define NEURON_TYPE             3
    #define NEURON_INDICES          4


network_t * parse_net_map(uint32_t *data) {
    network_t *net = (network_t*)calloc(1, sizeof(network_t));
    net->num_inputs = data[NET_NUM_INPUTS];
    net->num_neurons = data[NET_SIZE] - data[NET_NUM_INPUTS];
    net->num_outputs = data[NET_NUM_OUTPUTS];
    net->size = data[NET_SIZE];
    // printf("Network configuration: num_inputs: %d, net_size: %d, num_outputs: %d\n", net->num_inputs, net->size, net->num_outputs);
    net->arr = (double*)calloc(net->size, sizeof(double));
    net->bp_errors = (backprop_error_t*)calloc(net->size, sizeof(backprop_error_t));
    net->neurons = (neuron_t*)calloc(net->num_neurons, sizeof(neuron_t));
    net->output_indices = (uint32_t*)calloc(net->num_outputs, sizeof(uint32_t));
    net->outputs = (double*)calloc(net->num_outputs, sizeof(double));
    net->input_errors = (double*)calloc(net->num_inputs, sizeof(double));
    net->mutated_neuron_idx = 0;
    // net->micronets = NULL;
    
    for(uint32_t i=0; i<net->num_outputs; i++) {
        net->output_indices[i] = data[NET_OUTPUT_INDICES+i];
    }
    uint32_t *neurons = &data[NET_NEURONS+net->num_outputs];
    uint32_t offset = 0;
    for(uint32_t i=0; i<net->num_neurons; i++) {
        neuron_description_t *n = (neuron_description_t *)&neurons[offset];
        neuron_create(&net->neurons[i], n);
        offset += n->desc_size;
    }
    return net;
}

network_t *unpack_network_description(uint32_t data[]) {
    network_t *net = parse_net_map(data);
    net->is_micronet = 0;
    return net;
}