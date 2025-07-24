import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error
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
        error_threshold = 0.001
        rng_seed = 1751501246

        dll_loader = LoaderIface()
        network = NetworkInterface(get_network_arch(**network_architecture), dll_loader)
        network.init_rng(rng_seed)
        error = get_network_error(expected_outputs, network.get_outputs(net_inputs, 4))
        counter = 0
        while error > error_threshold:
            network.mutate(0.1)
            new_error = get_network_error(expected_outputs, network.get_outputs(net_inputs, 4))
            if new_error > error:
                network.rollback()
            elif new_error < error:
                error = new_error
            counter += 1
            self.assertLess(counter, 1000)

        error = get_network_error(expected_outputs, network.get_outputs(net_inputs, 4))
        self.assertLess(error, error_threshold)


if __name__ == "__main__":
    unittest.main()