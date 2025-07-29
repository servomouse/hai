import sys
import os
import unittest
import numpy as np
import concurrent.futures
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, NeuronTypes
from python.dll_loader import LoaderIface


sentences = [
    # "A fallen tree is blocking the road.",
    # "The birds built their nest in the small fir tree.",
    # "The air was so still that not even the leaves on the trees were moving.",
    # "These trees will have to be cut down to make way for the new road.",
    # "A young boy climbed into the apple tree and shook the branches so that the fruit fell down.",
    # "The sun climbed higher in the sky.",
    # "They're advising that children be kept out of the sun altogether.",
    # "The clouds finally parted and the sun came out.",
    # "She left the midday sun for the cool of the shade.",
    # "Now I know it won't look very cool, but this hat will keep the sun out of your eyes.",
    # "We camped on one of the lower slopes of the mountain.",
    # "The view from the top of the mountain is breathtaking.",
    # "What's the highest mountain in Europe?",
    # "After three days lost in the mountains, all the climbers arrived home safe and sound.",
    # "They slowly ascended the steep path up the mountain.",
    # "The balloon rose gently (up) into the air.",
    # "The volcano spewed a giant cloud of ash, dust, and gases into the air.",
    # "The extent of the flooding can only be fully appreciated when viewed from the air.",
    # "The ball carried high into the air and landed the other side of the fence.",
    # "A cloud of dust rose in the air as the car roared past.",
    # "It's the dampness in the air that is bad for your lungs.",
    # "He let the air out of the balloon.",
    # "The mountain air was wonderfully pure.",
    # "There was a rush of air as she opened the door.",
    # "Stricter controls on air pollution would help to reduce acid rain.",
    # "Warm air rises by the process of convection.",
    # "She's studying modern Japanese language and culture.",
    "Unable to speak a word of the language, he communicated with his hands.",
    "We were encouraged to learn foreign languages at school.",
    "Her novels have been translated into 19 languages.",
    "One of the main reasons I came to England was to study the language.",
    "Our neighbours are very inconsiderate - they're always playing loud music late at night.",
    "Listening to music is one of his greatest joys.",
    "I find some of Brahms's music deeply moving.",
    "She composes and performs her own music.",
    "Do you mind if I put some music on?",
    "American culture has been exported all over the world.",
    "She got some books out of the library and immersed herself in Jewish history and culture.",
    "Each culture had a special ritual to initiate boys into manhood.",
    "Surely it is wrong to try to impose western culture on other countries?",
    "It's a nostalgia trip back into the swinging culture of the 1960s.",
    "Do you think there is a culture of lying within modern politics?",
    "I was suffering from an overdose of culture.",
    "She's the personification of culture and refinement.",
    "The advertising industry's use of classic songs is vandalism of popular culture, he said.",
    "There's not much here in the way of culture.",
    "Jane's hand on my shoulder woke me from a bad dream.",
    "I was in the middle of an amazing dream when the alarm went off.",
    "Some people believe that dreams reveal important things about your subconscious thoughts.",
    "I had a weird dream about you last night.",
    "If I eat a lot of cheese in the evening, I have amazing dreams.",
    "I always like to leave my desk clear at the end of the day.",
    "We went to Edinburgh and back again all in one day.",
    "We're open every day except Sunday.",
    "She had five days off work due to illness.",
    "The soldiers marched 90 miles in three days.",
]

def string_to_binary_array(input_string):
    # Convert the string to a 2d array which is a binary representation of the string (16 bit wide)
    binary_strings = [format(ord(char), '016b') for char in input_string]
    binary_array = [[int(bit) for bit in binary] for binary in binary_strings]
    return binary_array


def binary_array_to_string(binary_array):
    # Convert each row of the binary array to a character
    characters = []
    for row in binary_array:
        binary_string = ''.join(str(bit) for bit in row)
        character = chr(int(binary_string, 2))
        characters.append(character)
    return ''.join(characters)


def float_to_bin(value):
    if value > 0.5:
        return 1
    return 0


def float_to_binary_array(float_array):
    bin_array = []
    for i in float_array:
        bin_array.append([float_to_bin(a) for a in i])
    return bin_array


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


def save_arch_to_file(network_arch, filename):
    with open(filename, 'w') as f:
        f.write(f"num_inputs: {network_arch['num_inputs']},\n")
        f.write(f"neurons: [\n")
        for n in network_arch['neurons']:
            f.write(f"\t{n},\n")
        f.write(f"],\n")
        f.write(f"output_indices: {network_arch['output_indices']}\n")


def get_net_arch(arch):
    # example_arch = [
    #     {"size": 16, "type": "input", "inputs": None},
    #     {"size": 16*16, "type": "hidden", "inputs": [0, 3]},
    #     {"size": 16*16, "type": "hidden", "inputs": [1]},
    #     {"size": 16*16, "type": "output", "inputs": [2]},
    # ]
    # arch = example_arch
    net_arch = {
        "num_inputs": 0,
        "neurons": [],
        "output_indices": []
    }
    # Calculate indices
    indices = []
    idx = 0
    for layer in arch:
        indices.append([i+idx for i in range(layer["size"])])
        idx += layer["size"]
        if layer["type"] == "output":
            net_arch['output_indices'].extend(indices[-1])
    # Calculate inputs indices
    inputs = []
    for i in range(len(arch)):
        if arch[i]["inputs"] is None:
            inputs.append([])
        else:
            temp = []
            for a in arch[i]["inputs"]:
                temp.extend(indices[a])
            inputs.append(temp)

    for i in range(len(arch)):
        if arch[i]["type"] == "input":
            net_arch['num_inputs'] += arch[i]["size"]
        else:
            for a in range(arch[i]["size"]):
                net_arch['neurons'].append(
                    {"idx": indices[i][a], "type": int(NeuronTypes.Linear), "input_indices": inputs[i]}
                )
    # with open("encoder_arch.txt", 'w') as f:
    #     f.write(f"num_inputs: {net_arch['num_inputs']},\n")
    #     f.write(f"neurons: [\n")
    #     for n in net_arch['neurons']:
    #         f.write(f"\t{n},\n")
    #     f.write(f"],\n")
    #     f.write(f"output_indices: {net_arch['output_indices']}\n")
    return net_arch


def net_get_output(encoder, decoder, v_in):
    z_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    n_steps = len(v_in)
    for symbol in v_in:
        encoder.get_outputs(symbol, 256)
    v_irt = encoder.get_outputs(z_array, 256)
    v_in.append(z_array)
    v_out = []
    for _ in range(n_steps):
        v_out.append(decoder.get_outputs(v_irt, 16))
    v_out.append(decoder.get_outputs(v_irt, 16))
    return v_out


def get_net_error(encoder, decoder, dataset):
    error_counter = 0
    error = 0
    for s in dataset:
        v_in = string_to_binary_array(s)
        v_out = net_get_output(encoder, decoder, v_in)
        error += get_network_error(v_in, v_out)
        error_counter += 1
        encoder.clean()
        decoder.clean()
    return error/error_counter


class TestClassName(unittest.TestCase):
    def test_evolution(self):
        encoder_arch = get_net_arch([
            {"size": 16, "type": "input", "inputs": None},
            {"size": 16*16, "type": "hidden", "inputs": [0, 3]},
            {"size": 16*16, "type": "hidden", "inputs": [1]},
            {"size": 16*16, "type": "output", "inputs": [2]},
        ])
        decoder_arch = get_net_arch([
            {"size": 16*16, "type": "input", "inputs": None},
            {"size": 16*16, "type": "hidden", "inputs": [0, 3]},
            {"size": 16*16, "type": "hidden", "inputs": [1]},
            {"size": 16*16, "type": "hidden", "inputs": [2]},
            {"size": 16, "type": "output", "inputs": [3]},
        ])
        # save_arch_to_file(encoder_arch, "encoder_arch.txt")
        # save_arch_to_file(decoder_arch, "decoder_arch.txt")
        rng_seed = 1751501246

        dll_loader = LoaderIface()
        encoder = NetworkInterface(get_network_arch(**encoder_arch), dll_loader)
        decoder = NetworkInterface(get_network_arch(**decoder_arch), dll_loader)
        # encoder.init_rng(rng_seed)  # Use a seed for consistency
        # decoder.init_rng(rng_seed)  # Use a seed for consistency
        # print(f"{encoder.get_num_neurons() = }")
        # print(f"{decoder.get_num_neurons() = }")
        encoder.network_restore_coeffs("encoder_coeffs.txt")
        decoder.network_restore_coeffs("decoder_coeffs.txt")
        nets = [encoder, decoder]
        min_error = get_net_error(encoder, decoder, sentences)
        selector = 0
        print(f"Initial error: {min_error}")
        for lap in range(10000):
            print(f"\rRunning {lap}'th round . . .", end='')
            nets[selector].mutate(0.1)
            new_error = get_net_error(encoder, decoder, sentences)
            if new_error > min_error:
                nets[selector].rollback()
            elif new_error < min_error:
                min_error = new_error
                print(f"\t{new_error = }")
            if (lap % 100) == 0:
                encoder.network_save_coeffs("encoder_coeffs.txt")
                decoder.network_save_coeffs("decoder_coeffs.txt")
                print("Coeffs saved")
            if selector == 0:
                selector = 1
            else:
                selector = 0
            if (lap % 1000) == 0:
                in_str = random.choice(sentences)
                outputs = net_get_output(encoder, decoder, string_to_binary_array(in_str))
                out_str = binary_array_to_string(float_to_binary_array(outputs))
                print(f"\tInput string: {in_str}; output string: {out_str}")

        in_str = random.choice(sentences)
        outputs = net_get_output(encoder, decoder, string_to_binary_array(in_str))
        out_str = binary_array_to_string(float_to_binary_array(outputs))
        print(f"\tInput string: {in_str}; output string: {out_str}")

        print(f"\tFinal error: {min_error}")
        encoder.network_save_coeffs("encoder_coeffs.txt")
        decoder.network_save_coeffs("decoder_coeffs.txt")

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
        # get_encoder_architecture()
        # get_decoder_architecture()
        self.assertLess(1, 2)


if __name__ == "__main__":
    unittest.main()
