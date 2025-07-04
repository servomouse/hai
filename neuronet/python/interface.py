import ctypes
import numpy as np

class NetworkInterface:
    def __init__(self, dll_path, net_arch_path):
        # Load the shared library
        self.dll = ctypes.CDLL(dll_path)

        # Read the network architecture from the file
        self.net_arch = self._read_net_arch(net_arch_path)

        # Create the network
        self.dll.network_create((ctypes.c_uint32 * len(self.net_arch))(*self.net_arch))

    def _read_net_arch(self, net_arch_path):
        with open(net_arch_path, 'r') as file:
            # Assuming the file contains a list of integers
            return [int(line.strip()) for line in file.readlines()]

    def get_outputs(self, inputs):
        # Convert inputs to a ctypes array
        input_array = (ctypes.c_double * len(inputs))(*inputs)
        # Call the C function
        output_ptr = self.dll.network_get_outputs(input_array)
        # Convert the output pointer to a Python list
        output_list = []
        # Assuming the output is a fixed size, you may need to adjust this
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
        # Call the C function to get coefficients
        coeffs_ptr = self.dll.network_get_coeffs(ctypes.c_uint32(idx))
        # Convert the C string to a Python string
        coeffs_str = ctypes.string_at(coeffs_ptr).decode('utf-8')
        # Free the memory allocated for the string (if necessary)
        self.dll.free(coeffs_ptr)  # Assuming there's a free function in the DLL
        return coeffs_str

    def set_coeffs(self, idx, values):
        # Convert values to a ctypes array
        values_array = (ctypes.c_double * len(values))(*values)
        self.dll.network_set_coeffs(ctypes.c_uint32(idx), values_array)

# Example usage:
# network = NetworkInterface('path/to/your.dll', 'path/to/net_arch.txt')
# outputs = network.get_outputs([0.5, 0.2, 0.1])
# network.mutate(0.05)
# coeffs = network.get_coeffs(0)
# network.set_coeffs(0, [0.1, -0.2, 0.3])