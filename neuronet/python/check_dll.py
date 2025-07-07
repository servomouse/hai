import pefile   # pip install pefile
import platform

def get_bittness(value):
    if '64' in value:
        return 64
    if '32' in value:
        return 32
    raise Exception(f"Error: Unknown bittness: {value}")

def get_dll_bitness(dll_path):
    try:
        pe = pefile.PE(dll_path)
        if pe.FILE_HEADER.Machine == pefile.MACHINE_TYPE['IMAGE_FILE_MACHINE_I386']:
            return "32-bit"
        elif pe.FILE_HEADER.Machine == pefile.MACHINE_TYPE['IMAGE_FILE_MACHINE_AMD64']:
            return "64-bit"
        else:
            return "Unknown bitness"
    except Exception as e:
        return f"Error: {e}"

def check_compatibility(dll_path):
    """ Raises exception on error """
    python_bitness = get_bittness(platform.architecture()[0])
    dll_bittness = get_bittness(get_dll_bitness(dll_path))
    if python_bitness != dll_bittness:
        raise Exception(F"Error: python and DLL bittness mismatch: python bittness: {python_bitness} bit, DLL bittness: {dll_bittness} bit")
