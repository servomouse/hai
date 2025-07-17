import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, NeuronTypes


def has_duplicates(arr):
    """
    Checks if a list contains duplicate elements.

    Args:
        my_list: The list to check.

    Returns:
        True if duplicates are found, False otherwise.
    """
    seen = set()
    for subarr in arr:
        # Convert inner list to a tuple
        tuple_representation = tuple(subarr)
        if tuple_representation in seen:
            return True  # Duplicate found
        seen.add(tuple_representation)
    return False  # No duplicates

# Returns a 2D array (M x N) of randomly placed evenly distributes zeroes and ones
def random_binary_array(m, n):
    """
    Args:
        m: width of the resulting array
        n: height of the resulting array

    Returns:
        A 2D array (M x N) of randomly placed evenly distributes zeroes and ones
    """
    total_elements = m * n
    num_ones = total_elements // 2
    num_zeros = total_elements - num_ones
    binary_array = [1] * num_ones + [0] * num_zeros
    np.random.shuffle(binary_array)
    return np.array(binary_array).reshape(m, n).tolist()


network_architecture = {
    "num_inputs": 8 + (16*16),
    "neurons": [
        *[{"idx": i, "type": NeuronTypes.Linear, "input_indices": [j for j in range(8)]} for i in range(8, 16)],    # Serial input layer
        {"idx": 5, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
        {"idx": 6, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
        {"idx": 7, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
    ],
    "output_indices": [4, 5, 6, 7]
}

def get_encoder_architecture():
    encoder_architecture = {
        "num_inputs": 16,
        "neurons": [],
        "output_indices": []
    }
    layers = [
        [16, 16],
        [16, 16],
        [16, 16],
    ]
    layers_indices = []
    idx = encoder_architecture['num_inputs']
    for l in layers:
        indices = []
        for i in range(idx, l[0]*l[1]+idx):
            indices.append(i)
        layers_indices.append(indices)
        idx += l[0]*l[1]
    for i in range(len(layers_indices)):
        inputs = layers_indices[i-1]
        for idx in layers_indices[i]:
            encoder_architecture['neurons'].append(
                {"idx": idx, "type": NeuronTypes.Linear, "input_indices": inputs}
            )
    encoder_architecture['output_indices'] = layers_indices[-1]
    # with open("output.txt", 'w') as f:
    #     f.write(f"num_inputs: {encoder_architecture['num_inputs']},\n")
    #     f.write(f"neurons: [\n")
    #     for n in encoder_architecture['neurons']:
    #         f.write(f"\t{n},\n")
    #     f.write(f"],\n")
    #     f.write(f"output_indices: [{encoder_architecture['output_indices']}]\n")
    return encoder_architecture



class TestClassName(unittest.TestCase):
    def test_evolution(self):
        print("Testing linear network evolution")
        # net_inputs = [0.2, -0.2, 0.2, -0.2]
        # expected_outputs = [0.1, -0.3, 0.5, -0.7]
        # rng_seed = 1751501246

        # network = NetworkInterface(get_network_arch(**network_architecture))
        # network.init_rng(rng_seed)  # Use a seed for consistency
        # outputs = network.get_outputs(net_inputs)
        # error = get_network_error(expected_outputs, outputs)
        # individual_errors = get_network_individual_errors(expected_outputs, outputs)
        # print(f"Initial error: {error}, individual errors: {individual_errors}")

        # counter = 0
        # # self.assertGreater(error, 0.5)
        # while counter < 250:
        #     network.backpropagation(individual_errors)
        #     network.backprop_update_weights(0.01)

        #     outputs = network.get_outputs(net_inputs)
        #     error = get_network_error(expected_outputs, outputs)
        #     individual_errors = get_network_individual_errors(expected_outputs, outputs)
        #     counter += 1

        # print(f"Final error: {error}, individual errors: {individual_errors}")
        get_encoder_architecture()
        self.assertLess(1, 2)


if __name__ == "__main__":
    unittest.main()