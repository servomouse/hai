# Plain test implementation

import hashlib
import random

input_text = """
The Signal from Svalbard
Elias sat in a small, cluttered apartment in Buenos Aires. On his desk lay an antique shortwave radio that once belonged to his grandfather. Despite the thousands of miles of distance, Elias used the radio to maintain a daily connection with Sina, a researcher stationed at the Svalbard Global Seed Vault in Norway.

The connection was not just digital or via radio waves; it was historical. Sina was studying a specific strain of Andean Maize that Elias had sent her three months ago via a global courier service. This seeds' journey had started in the Jujuy Province of Argentina, traveled through a sorting hub in Frankfurt, and finally arrived at the icy docks of Longyearbyen.

Yesterday, Sina discovered a unique genetic marker in the maize. She sent an encrypted data packet to Elias’s laptop. The data contained coordinates for a forgotten plantation located back in the Amazon Rainforest.

Elias looked at the map on his wall. He realized that the seeds in Norway, the researcher in the Arctic, and the hidden plantation in Brazil were all parts of the same ancient biological network. He picked up his phone and called Dr. Aris, a botanist at the University of São Paulo, to bridge the final gap in the circuit.
"""


def get_node_vector(input_string):
    """
    Generate a unique array of 1024 floats from a given input string.

    This function takes an input string, hashes it using the SHA-256 algorithm,
    and produces a deterministic array of floats. The output will be unique for 
    each distinct input string, while the same input string will always produce 
    the same output vector.

    Parameters:
    ----------
    input_string : str
        The input string from which the float array will be generated.

    Returns:
    -------
    numpy.ndarray
        A NumPy array containing 1024 floating-point values, normalized to the 
        range [0, 1). The values in the array are generated based on the hash
        of the input string and will change with different input strings.
    """
    hash_object = hashlib.sha256(input_string.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert hash to an integer
    hash_int = int(hash_hex, 16)
    random.seed(hash_int)
    
    # Create an array of 1024 floats based on the hashed integer
    float_vector = []
    for _ in range(1024):
        float_vector.append(random.random())
    
    return float_vector


def process_text(text):
    graph = {}
    for c in text:
        node = {
            "input_links": [],
            "output_links": [],
            "vector": get_node_vector(c)
        }

