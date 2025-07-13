import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface
from python.network import get_network_arch, NeuronTypes


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


def get_error(target, result):
    if len(target) != len(result):
        raise Exception(f"Error: target vs result outputs length mismatch!")
    error = 0
    for i in range(len(target)):
        error += (target[i] - result[i])**2
    return error / len(target)


class TestClassName(unittest.TestCase):
    def test_evolution(self):
        print("Testing linear network evolution")
        net_inputs = [0.2, -0.2, 0.2, -0.2]
        expected_outputs = [0.1, -0.3, 0.5, -0.7]
        error_threshold = 0.001
        rng_seed = 1751501246

        network = NetworkInterface(get_network_arch(**network_architecture))
        network.init_rng(rng_seed)
        error = get_error(expected_outputs, network.get_outputs(net_inputs))
        counter = 0
        while error > error_threshold:
            network.mutate(0.1)
            new_error = get_error(expected_outputs, network.get_outputs(net_inputs))
            if new_error > error:
                network.rollback()
            elif new_error < error:
                error = new_error
            counter += 1
            self.assertLess(counter, 1000)

        error = get_error(expected_outputs, network.get_outputs(net_inputs))
        self.assertLess(error, error_threshold)


if __name__ == "__main__":
    unittest.main()