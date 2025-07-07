import ctypes

c_types = {
    "void": None,
    "int": ctypes.c_int,
    "uint8_t": ctypes.c_uint8,
    "uint16_t": ctypes.c_uint16,
    "uint32_t": ctypes.c_uint32,
    "size_t": ctypes.c_size_t,
    "double": ctypes.c_double,
    "char": ctypes.c_char,
    # "char*": ctypes.c_char_p,
}
# ctypes.POINTER(ctypes.c_double)

def get_dll_function(dll_object, foo_name, signature):
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
            arg = ctypes.POINTER(c_types[arg])
        else:
            arg = c_types[arg.strip()]
        foo_args.append(arg)
    
    if foo_args == [None]:
        foo_args = None
    
    print(f"{ret_type}, {foo_name}, {foo_args}")
    foo_attr = getattr(dll_object, foo_name)
    foo_attr.argtypes = foo_args
    foo_attr.restype = ret_type
    # self.lib.network_create.argtypes = (ctypes.POINTER(ctypes.c_uint32))
    # self.lib.network_create.restype = None
