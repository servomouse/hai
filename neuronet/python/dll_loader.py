import ctypes
import os
import shutil
import atexit
import sys
from .check_dll import check_compatibility
import subprocess

c_types = {
    "void": None,
    "int": ctypes.c_int,
    "uint8_t": ctypes.c_uint8,
    "uint16_t": ctypes.c_uint16,
    "uint32_t": ctypes.c_uint32,
    "size_t": ctypes.c_size_t,
    "double": ctypes.c_double,
    "char": ctypes.c_char,
}


class LoaderIface:
    def __init__(self):
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], shell=True, capture_output=True, text=True)
        project_root = f"{result.stdout.strip()}/neuronet"
        self.bin_folder = f"{project_root}/bin"

        self.filename_counter = {}
        self.copy_filenames = []
        atexit.register(self.cleanup)
        files = os.listdir(self.bin_folder)
        for f in files:
            if f.endswith("_deleted"):
                try:
                    os.remove(f"{self.bin_folder}/{f}")
                except: # If cannot remove - ignore
                    pass

    def upload(self, filename):
        # Check the dll:
        if not os.path.isfile(filename):
            raise Exception(f"Error: cannot open file ({filename})")
        check_compatibility(filename)

        if filename not in self.filename_counter:
            self.filename_counter[filename] = 0
            return ctypes.CDLL(filename)
        else:
            self.filename_counter[filename] += 1
            base, extension = os.path.splitext(filename)
            copy_filename = f"{base}_{self.filename_counter[filename]}{extension}"
            self.copy_filenames.append(copy_filename)
            if not os.path.exists(copy_filename):
                shutil.copy(filename, copy_filename)
            return ctypes.CDLL(copy_filename)

    def register_dll_function(self, dll_object, foo_name, signature):
        """
        Signature looks like this: uint32_t foo(double)
        Use "foo" as a function name for signature
        """
        ret_type, args = signature.split("foo")
        if ret_type.strip().endswith("*"):
            ret_type = ret_type.strip()[:-1].strip()
            ret_type = ctypes.POINTER(c_types[ret_type])
        else:
            ret_type = c_types[ret_type.strip()]
        args = args.strip()[1:-1].split(", ")
        foo_args = []
        for arg in args:
            arg = arg.strip()
            if arg.endswith("*"):
                arg = arg[:-1].strip()
                if arg == "void":
                    arg = ctypes.c_void_p
                else:
                    arg = ctypes.POINTER(c_types[arg])
            else:
                arg = c_types[arg.strip()]
            foo_args.append(arg)
        
        if foo_args == [None]:
            foo_args = None

        foo_attr = getattr(dll_object, foo_name)
        foo_attr.argtypes = foo_args
        foo_attr.restype = ret_type

    def cleanup(self):
        print("Running cleanup...")
        for filename in self.copy_filenames:
            # Cannot delete, but can rename. Will be deleted at next start
            os.replace(filename, filename + '_deleted')
