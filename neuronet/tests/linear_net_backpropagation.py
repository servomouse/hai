import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, NeuronTypes
from python.dll_loader import LoaderIface




class TestClassName(unittest.TestCase):
    def test_evolution_1_layer(self):
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

        print("Testing linear network backpropagation for 1 layer")
        net_inputs = [0.2, -0.2, 0.2, -0.2]
        expected_outputs = [0.1, -0.3, 0.5, -0.7]
        rng_seed = 1751501246

        dll_loader = LoaderIface()
        network = NetworkInterface(get_network_arch(**network_architecture), dll_loader, rng_seed=rng_seed) # Use a seed for consistency
        outputs = network.get_outputs(net_inputs, 4)
        error = get_network_error(expected_outputs, outputs)
        individual_errors = get_network_individual_errors(expected_outputs, outputs)
        print(f"Initial error: {error}, individual errors: {individual_errors}, outputs: {outputs}")

        counter = 0
        self.assertGreater(error, 0.05)
        while counter < 250:
            network.backpropagation(individual_errors)
            network.backprop_update_weights(0.01)

            outputs = network.get_outputs(net_inputs, 4)
            error = get_network_error(expected_outputs, outputs)
            individual_errors = get_network_individual_errors(expected_outputs, outputs)
            counter += 1

        print(f"Final error: {error}, individual errors: {individual_errors}, outputs: {outputs}")

        self.assertLess(error, 0.0002)

    def test_evolution_2_layers(self):
        network_architecture = {
            "num_inputs": 4,
            "neurons": [
                {"idx": 4, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
                {"idx": 5, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
                {"idx": 6, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
                {"idx": 7, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
                {"idx":  8, "type": NeuronTypes.Linear, "input_indices": [4, 5, 6, 7]},
                {"idx":  9, "type": NeuronTypes.Linear, "input_indices": [4, 5, 6, 7]},
                {"idx": 10, "type": NeuronTypes.Linear, "input_indices": [4, 5, 6, 7]},
                {"idx": 11, "type": NeuronTypes.Linear, "input_indices": [4, 5, 6, 7]},
            ],
            "output_indices": [8, 9, 10, 11]
        }

        print("Testing linear network backpropagation for 2 layers")
        # net_inputs = [0.1, -0.1, 0.1, -0.1]
        # # expected_outputs = [0.1, -0.3, 0.5, -0.7]
        # expected_outputs = [-0.5, 0.6, -0.7, 0.8]
        dataset = [
            [[0.1, -0.1, 0.1, -0.1], [-0.5, 0.6, -0.7, 0.8]],
            [[-0.1, 0.1, -0.1, 0.1], [0.5, -0.6, 0.7, -0.8]],
            [[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
        ]
        rng_seed = 1751501246

        dll_loader = LoaderIface()
        network = NetworkInterface(get_network_arch(**network_architecture), dll_loader, rng_seed=rng_seed) # Use a seed for consistency

        counter = 0
        h = 0.01
        while counter < 700:
            error = 0
            outputs_arr = []
            for d in dataset:
                outputs = network.get_outputs(d[0], 4)
                outputs_arr.append(outputs)
                error += get_network_error(d[1], outputs)
                individual_errors = get_network_individual_errors(d[1], outputs)

                network.backpropagation(individual_errors)
            if counter == 0:
                print(f"Initial error: {error}")
            error /= len(dataset)
            # if (counter > 0) and ((counter % 100) == 0):
            #     h /= 10
            network.backprop_update_weights(h)
            counter += 1

        print(f"Final error: {error}, outputs: {outputs_arr}")
        for i in range(len(dataset)):
            print(f"Inputs: {dataset[i][0]}, target: {dataset[i][1]}, outputs: {outputs_arr[i]}")

        self.assertLess(error, 0.0001)


if __name__ == "__main__":
    unittest.main()