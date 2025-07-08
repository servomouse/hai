import ctypes
import numpy as np
import os
from check_dll import check_compatibility
from dll_loader import get_dll_function

network_dll_path = 'D:\\Work\\Projects\\HAI\\neuronet\\bin\\libnetwork.dll'

dll_interface = {
    "network_create":       "void foo(uint32_t *)",
    "network_get_outputs":  "double * foo(double *)",
    "network_mutate":       "void foo(double)",
    "network_rollback":     "void foo(void)",
    "network_get_coeffs":   "char * foo(uint32_t)",
    "network_set_coeffs":   "void foo(uint32_t, double *)",
    "network_free":         "void foo(void *)",
}

network_arch = [
    # Network_config:
    # 0,  # Num micronets
    40, # Main net description size
    4,  # Net num inputs
    8,  # Net size
    4,  # Net num outputs
    4,  # Net output indices:
    5,
    6,
    7,
    # Neurons:
    #  Size    idx num_inputs  type    indices:
        8,      4,  4,          0,      0, 1, 2, 3,
        8,      5,  4,          0,      0, 1, 2, 3,
        8,      6,  4,          0,      0, 1, 2, 3,
        8,      7,  4,          0,      0, 1, 2, 3,
]

class NetworkInterface:
    def __init__(self, dll_path, net_arch_path):
        # Check the dll"
        if not os.path.isfile(dll_path):
            raise Exception(f"Error: cannot open file ({dll_path})")
        check_compatibility(network_dll_path)

        self.network = ctypes.CDLL(dll_path)
        self.net_arch = network_arch

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


def main():
    final_coeffs = [
        [-0.371300, -0.438380, -0.519600, 0.444090, 0.280620],
        [-0.957770, 0.977300, 0.133530, -0.596600, -0.059860],
        [-0.817640, -0.108050, 0.704190, -0.780050, 0.341150],
        [-0.171120, 0.210090, 0.009990, 0.852520, -0.512110]
    ]
    net_inputs = [0.2, -0.2, 0.2, -0.2]
    network = NetworkInterface(network_dll_path, 'path/to/net_arch.txt')
    outputs = network.get_outputs(net_inputs)
    print(f"Network outputs: {outputs}")
    print("Network coeffitients:")
    for i in range(4):
        coeffs = network.get_coeffs(i)
        print(f"\t{i}: {coeffs}")
    network.mutate(0.1)
    outputs = network.get_outputs(net_inputs)
    print(f"Network outputs: {outputs}")
    print("Network coeffitients:")
    for i in range(4):
        coeffs = network.get_coeffs(i)
        print(f"\t{i}: {coeffs}")

    for i in range(len(final_coeffs)):
        network.set_coeffs(i, final_coeffs[i])

    outputs = network.get_outputs(net_inputs)
    print(f"Network outputs: {outputs}")
    print("Network coeffitients:")
    for i in range(4):
        coeffs = network.get_coeffs(i)
        print(f"\t{i}: {coeffs}")
    # network.set_coeffs(0, [0.1, -0.2, 0.3])


if __name__ == "__main__":
    main()
