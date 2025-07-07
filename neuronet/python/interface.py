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
}

network_arch = [
    # Network_config:
    0,  # Num micronets
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

        self.network.network_create((ctypes.c_uint32 * len(self.net_arch))(*self.net_arch))
    
    def init_functions(self, lib_path):
        self.lib = ctypes.CDLL(lib_path)

        self.lib.network_create.argtypes = (ctypes.POINTER(ctypes.c_uint32))
        self.lib.network_create.restype = None

        self.lib.print_double_array.argtypes = (ctypes.POINTER(ctypes.c_double), ctypes.c_size_t)
        self.lib.print_double_array.restype = None

        self.lib.network_get_outputs.argtypes = (ctypes.POINTER(ctypes.c_double),)
        self.lib.network_get_outputs.restype = ctypes.POINTER(ctypes.c_double)

        self.lib.network_mutate.argtypes = (None,)
        self.lib.network_mutate.restype = None
        self.lib.network_rollback.argtypes = (None,)
        self.lib.network_rollback.restype = None

        # Double array as a return value:
        #   double_array_pointer = lib.create_double_array(5)
        #   double_array = np.ctypeslib.as_array(double_array_pointer, shape=(size,))

        # Double array as an argument:
        # double_array = np.array([1.1, 2.2, 3.3, 4.4, 5.5], dtype=np.double)
        # double_array_pointer = double_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        # lib.print_double_array(double_array_pointer, double_array.size)

        # Array of uint32_t as an argument:
        # uint32_array = np.array([1, 2, 3, 4, 5], dtype=np.uint32)
        # uint32_array_pointer = uint32_array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))
        # lib.print_uint32_array(uint32_array_pointer, uint32_array.size)

    # def _read_net_arch(self, net_arch_path):
    #     with open(net_arch_path, 'r') as file:
    #         # Assuming the file contains a list of integers
    #         return [int(line.strip()) for line in file.readlines()]

    def get_outputs(self, inputs):
        input_array = (ctypes.c_double * len(inputs))(*inputs)
        output_ptr = self.dll.network_get_outputs(input_array)
        output_list = []
        for i in range(len(inputs)):  # Adjust the range as needed
            output_list.append(output_ptr[i])
        return output_list

    def mutate(self, mutation_step):
        if 0 <= mutation_step <= 1:
            self.dll.network_mutate(ctypes.c_double(mutation_step))
        else:
            raise ValueError("mutation_step must be between 0 and 1")

    def rollback(self):
        self.dll.network_rollback()

    def get_coeffs(self, idx):
        coeffs_ptr = self.dll.network_get_coeffs(ctypes.c_uint32(idx))
        coeffs_str = ctypes.string_at(coeffs_ptr).decode('utf-8')
        self.dll.free(coeffs_ptr)  # Assuming there's a free function in the DLL
        return coeffs_str

    def set_coeffs(self, idx, values):
        values_array = (ctypes.c_double * len(values))(*values)
        self.dll.network_set_coeffs(ctypes.c_uint32(idx), values_array)


def main():
    network = NetworkInterface(network_dll_path, 'path/to/net_arch.txt')
    outputs = network.get_outputs([0.5, 0.2, 0.1])
    # network.mutate(0.05)
    # coeffs = network.get_coeffs(0)
    # network.set_coeffs(0, [0.1, -0.2, 0.3])


if __name__ == "__main__":
    main()
