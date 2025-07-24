import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, NeuronTypes
from python.dll_loader import LoaderIface


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


class TestClassName(unittest.TestCase):
    def test_evolution(self):
        print("Testing linear network evolution")
        net_inputs = [0.2, -0.2, 0.2, -0.2]
        expected_outputs = [0.1, -0.3, 0.5, -0.7]
        rng_seed = 1751501246

        dll_loader = LoaderIface()
        network = NetworkInterface(get_network_arch(**network_architecture), dll_loader)
        network.init_rng(rng_seed)  # Use a seed for consistency
        outputs = network.get_outputs(net_inputs, 4)
        error = get_network_error(expected_outputs, outputs)
        individual_errors = get_network_individual_errors(expected_outputs, outputs)
        print(f"Initial error: {error}, individual errors: {individual_errors}")

        counter = 0
        self.assertGreater(error, 0.5)
        while counter < 250:
            network.backpropagation(individual_errors)
            network.backprop_update_weights(0.01)

            outputs = network.get_outputs(net_inputs, 4)
            error = get_network_error(expected_outputs, outputs)
            individual_errors = get_network_individual_errors(expected_outputs, outputs)
            counter += 1

        print(f"Final error: {error}, individual errors: {individual_errors}")

        self.assertLess(error, 0.0001)


if __name__ == "__main__":
    unittest.main()