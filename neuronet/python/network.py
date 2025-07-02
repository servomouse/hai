import ctypes
import numpy as np


class NeuroNet:
    def __init__(self, arch):
        self.arch = arch
    
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

    
    def get_output(self, data):
        pass
    
    def mutate(self):
        pass
    
    def rollback(self):
        pass
    
    def store(self, filename):
        pass