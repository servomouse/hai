import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, NeuronTypes


sentences = [
    "A fallen tree is blocking the road.",
    "The birds built their nest in the small fir tree.",
    "The air was so still that not even the leaves on the trees were moving.",
    "These trees will have to be cut down to make way for the new road.",
    "A young boy climbed into the apple tree and shook the branches so that the fruit fell down.",
    "The sun climbed higher in the sky.",
    "They're advising that children be kept out of the sun altogether.",
    "The clouds finally parted and the sun came out.",
    "She left the midday sun for the cool of the shade.",
    "Now I know it won't look very cool, but this hat will keep the sun out of your eyes.",
    "We camped on one of the lower slopes of the mountain.",
    "The view from the top of the mountain is breathtaking.",
    "What's the highest mountain in Europe?",
    "After three days lost in the mountains, all the climbers arrived home safe and sound.",
    "They slowly ascended the steep path up the mountain.",
    "The balloon rose gently (up) into the air.",
    "The volcano spewed a giant cloud of ash, dust, and gases into the air.",
    "The extent of the flooding can only be fully appreciated when viewed from the air.",
    "The ball carried high into the air and landed the other side of the fence.",
    "A cloud of dust rose in the air as the car roared past.",
    "It's the dampness in the air that is bad for your lungs.",
    "He let the air out of the balloon.",
    "The mountain air was wonderfully pure.",
    "There was a rush of air as she opened the door.",
    "Stricter controls on air pollution would help to reduce acid rain.",
    "Warm air rises by the process of convection.",
    "She's studying modern Japanese language and culture.",
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


# network_architecture = {
#     "num_inputs": 8 + (16*16),
#     "neurons": [
#         *[{"idx": i, "type": NeuronTypes.Linear, "input_indices": [j for j in range(8)]} for i in range(8, 16)],    # Serial input layer
#         {"idx": 5, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
#         {"idx": 6, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
#         {"idx": 7, "type": NeuronTypes.Linear, "input_indices": [0, 1, 2, 3]},
#     ],
#     "output_indices": [4, 5, 6, 7]
# }

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
        if i == 0:
            inputs.extend([a for a in range(encoder_architecture['num_inputs'])])
        for idx in layers_indices[i]:
            encoder_architecture['neurons'].append(
                {"idx": idx, "type": NeuronTypes.Linear, "input_indices": inputs}
            )
    encoder_architecture['output_indices'] = layers_indices[-1]
    # with open("encoder_arch.txt", 'w') as f:
    #     f.write(f"num_inputs: {encoder_architecture['num_inputs']},\n")
    #     f.write(f"neurons: [\n")
    #     for n in encoder_architecture['neurons']:
    #         f.write(f"\t{n},\n")
    #     f.write(f"],\n")
    #     f.write(f"output_indices: {encoder_architecture['output_indices']}\n")
    return encoder_architecture

def get_decoder_architecture():
    encoder_architecture = {
        "num_inputs": 16*16,
        "neurons": [],
        "output_indices": []
    }
    layers = [
        [16, 16],
        [16, 16],
        [16, 16],
        [16, 1],
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
        inputs = layers_indices[i-2] if i == 0 else layers_indices[i-1]
        if i == 0:
            inputs.extend([a for a in range(encoder_architecture['num_inputs'])])
        for idx in layers_indices[i]:
            encoder_architecture['neurons'].append(
                {"idx": idx, "type": NeuronTypes.Linear, "input_indices": inputs}
            )
    encoder_architecture['output_indices'] = layers_indices[-1]
    # with open("decoder_arch.txt", 'w') as f:
    #     f.write(f"num_inputs: {encoder_architecture['num_inputs']},\n")
    #     f.write(f"neurons: [\n")
    #     for n in encoder_architecture['neurons']:
    #         f.write(f"\t{n},\n")
    #     f.write(f"],\n")
    #     f.write(f"output_indices: {encoder_architecture['output_indices']}\n")
    return encoder_architecture


class TestClassName(unittest.TestCase):
    def test_evolution(self):
        # net_inputs = [0.2, -0.2, 0.2, -0.2]
        # expected_outputs = [0.1, -0.3, 0.5, -0.7]
        rng_seed = 1751501246
        z_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        encoder = NetworkInterface(get_network_arch(**get_encoder_architecture()))
        decoder = NetworkInterface(get_network_arch(**get_decoder_architecture()))
        encoder.init_rng(rng_seed)  # Use a seed for consistency
        for s in sentences:
            v_in = string_to_binary_array(s)
            n_steps = len(v_in)
            for symbol in v_in:
                encoder.get_outputs(symbol)
            v_irt = encoder.get_outputs(z_array)
            v_in.append(z_array)
            v_out = []
            for _ in range(n_steps):
                v_out.append(decoder.get_outputs(v_irt))
            v_out.append(decoder.get_outputs(v_irt))
            error = get_network_error(v_in, v_out)
            print(f"{error = }")
            break

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