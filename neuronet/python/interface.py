import ctypes
import numpy as np
import os
from .check_dll import check_compatibility
from .dll_loader import get_dll_function
from .network import get_network_arch, NeuronTypes

network_dll_path = 'D:\\Work\\Projects\\HAI\\neuronet\\bin\\libnetwork.dll'

dll_interface = {
    "network_create":                   "void foo(uint32_t *)",
    "network_get_outputs":              "double * foo(double *)",
    "network_mutate":                   "void foo(double)",
    "network_init_rng":                 "void foo(size_t)",
    "network_rollback":                 "void foo(void)",
    "network_get_coeffs":               "char * foo(uint32_t)",
    "network_set_coeffs":               "void foo(uint32_t, double *)",
    "network_free":                     "void foo(void *)",
    "network_backpropagation":          "void foo(double *)",
    "network_backprop_update_weights":  "void foo(double)",
}

network_architecture = {
    "num_inputs": 4,
    "neurons": [
        {"idx": 4, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
        {"idx": 5, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
        {"idx": 6, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
        {"idx": 7, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
    ],
    "output_indices": [4, 5, 6, 7]
}


def get_network_error(target, result):
    if len(target) != len(result):
        raise Exception(f"Error: target vs result outputs length mismatch!")
    error = 0
    for i in range(len(target)):
        error += (target[i] - result[i])**2
    return error / len(target)


def get_network_individual_errors(target, result):
    """ Returns an array with errors of each output """
    if len(target) != len(result):
        raise Exception(f"Error: target vs result outputs length mismatch!")
    errors = []
    for i in range(len(target)):
        errors.append(2 * (target[i] - result[i]))
    return errors


class NetworkInterface:
    def __init__(self, net_arch):
        self.dll_path = 'D:\\Work\\Projects\\HAI\\neuronet\\bin\\libnetwork.dll'
        # Check the dll"
        if not os.path.isfile(self.dll_path):
            raise Exception(f"Error: cannot open file ({self.dll_path})")
        check_compatibility(self.dll_path)

        self.network = ctypes.CDLL(self.dll_path)
        self.net_arch = net_arch

        for function, signature in dll_interface.items():
            get_dll_function(self.network, function, signature)

        uint32_array = np.array(self.net_arch, dtype=np.uint32)
        uint32_array_pointer = uint32_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        self.network.network_create(uint32_array_pointer, uint32_array.size)

    def get_outputs(self, inputs):
        input_array = (ctypes.c_double * len(inputs))(*inputs)
        output_ptr = self.network.network_get_outputs(input_array)
        output_list = []
        for i in range(len(inputs)):  # Adjust the range as needed
            output_list.append(output_ptr[i])
        return output_list

    def init_rng(self, rng_seed):
        self.network.network_init_rng(ctypes.c_size_t(rng_seed))

    def mutate(self, mutation_step):
        if 0 <= mutation_step <= 1:
            self.network.network_mutate(ctypes.c_double(mutation_step))
        else:
            raise ValueError("mutation_step must be between 0 and 1")

    def rollback(self):
        self.network.network_rollback()

    def get_coeffs(self, idx):
        coeffs_ptr = self.network.network_get_coeffs(ctypes.c_uint32(idx))
        coeffs_str = ctypes.string_at(coeffs_ptr).decode('utf-8')
        self.network.network_free(coeffs_ptr)  # Assuming there's a free function in the DLL
        return coeffs_str

    def set_coeffs(self, idx, values):
        values_array = (ctypes.c_double * len(values))(*values)
        self.network.network_set_coeffs(ctypes.c_uint32(idx), values_array)
    
    def backpropagation(self, errors):
        errors_array = (ctypes.c_double * len(errors))(*errors)
        self.network.network_backpropagation(errors_array)
    
    def backprop_update_weights(self, learning_rate):
        self.network.network_backprop_update_weights(ctypes.c_double(learning_rate))


def main():
    final_coeffs = [
        [-0.371300, -0.438380, -0.519600, 0.444090, 0.280620],
        [-0.957770, 0.977300, 0.133530, -0.596600, -0.059860],
        [-0.817640, -0.108050, 0.704190, -0.780050, 0.341150],
        [-0.171120, 0.210090, 0.009990, 0.852520, -0.512110]
    ]
    net_inputs = [0.2, -0.2, 0.2, -0.2]

    network = NetworkInterface(get_network_arch(**network_architecture))
    outputs = network.get_outputs(net_inputs)
    print(f"Network outputs: {outputs}")
    print("Network coeffitients:")
    for i in range(4):
        coeffs = network.get_coeffs(i)
        print(f"\t{i}: {coeffs}")
    # network.mutate(0.1)
    # outputs = network.get_outputs(net_inputs)
    # print(f"Network outputs: {outputs}")
    # print("Network coeffitients:")
    # for i in range(4):
    #     coeffs = network.get_coeffs(i)
    #     print(f"\t{i}: {coeffs}")

    for i in range(len(final_coeffs)):
        network.set_coeffs(i, final_coeffs[i])

    outputs = network.get_outputs(net_inputs)
    print(f"Network outputs: {outputs}")
    print("Network coeffitients:")
    for i in range(4):
        coeffs = network.get_coeffs(i)
        print(f"\t{i}: {coeffs}")


if __name__ == "__main__":
    main()
