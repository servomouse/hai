import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error
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


class TestClassName(unittest.TestCase):
    def test_method(self):
        print("Testing linear network instantiation")
        final_coeffs = [
            [-0.371300, -0.438380, -0.519600, 0.444090, 0.280620],
            [-0.957770, 0.977300, 0.133530, -0.596600, -0.059860],
            [-0.817640, -0.108050, 0.704190, -0.780050, 0.341150],
            [-0.171120, 0.210090, 0.009990, 0.852520, -0.512110]
        ]
        net_inputs = [0.2, -0.2, 0.2, -0.2]
        expected_outputs = [0.1, -0.3, 0.5, -0.7]

        network = NetworkInterface(get_network_arch(**network_architecture))
        outputs = network.get_outputs(net_inputs)
        for i in range(4):
            coeffs = network.get_coeffs(i)
            coeffs = [float(c) for c in coeffs[1:-1].split(", ")]
            for c in range(len(coeffs)):
                self.assertNotEqual(coeffs[c], final_coeffs[i][c])

        for i in range(len(final_coeffs)):
            network.set_coeffs(i, final_coeffs[i])

        outputs = network.get_outputs(net_inputs)
        for i in range(4):
            coeffs = network.get_coeffs(i)
            coeffs = [float(c) for c in coeffs[1:-1].split(", ")]
            for c in range(len(coeffs)):
                self.assertEqual(coeffs[c], final_coeffs[i][c])
        error = get_network_error(expected_outputs, outputs)
        self.assertGreater(error, 0.0008)
        self.assertLess(error, 0.0009)


if __name__ == "__main__":
    unittest.main()