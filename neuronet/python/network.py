from enum import IntEnum

class NeuronTypes(IntEnum):
    Linear  = 0
    Poly    = 1
    Pattern = 2


def get_network_arch(num_inputs, neurons, output_indices):
    net_size = num_inputs + len(neurons)
    net_arch = [
        0,
        num_inputs,
        net_size,
        len(output_indices),
        *output_indices
    ]
    for n in neurons:
        neuron = []
        neuron.append(0)
        neuron.append(n["idx"])
        neuron.append(len(n["input_indices"]))
        neuron.append(int(n["type"]))
        neuron.extend(n["input_indices"])
        neuron[0] = len(neuron)
        net_arch.extend(neuron)
    net_arch[0] = len(net_arch)
    return net_arch
