import sys
import os
import unittest
import numpy as np
import concurrent.futures
import random
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, NeuronTypes
from python.dll_loader import LoaderIface

encoded_width = 8


alphabet = {
    ' ': [0, 0, 0, 0, 0],   # 0
    'a': [0, 0, 0, 0, 1],   # 1
    'b': [0, 0, 0, 1, 0],   # 2
    'c': [0, 0, 0, 1, 1],   # 3
    'd': [0, 0, 1, 0, 0],   # 4
    'e': [0, 0, 1, 0, 1],   # 5
    'f': [0, 0, 1, 1, 0],   # 6
    'g': [0, 0, 1, 1, 1],   # 7
    'h': [0, 1, 0, 0, 0],   # 8
    'i': [0, 1, 0, 0, 1],   # 9
    'j': [0, 1, 0, 1, 0],   # 10
    'k': [0, 1, 0, 1, 1],   # 11
    'l': [0, 1, 1, 0, 0],   # 12
    'm': [0, 1, 1, 0, 1],   # 13
    'n': [0, 1, 1, 1, 0],   # 14
    'o': [0, 1, 1, 1, 1],   # 15
    'p': [1, 0, 0, 0, 0],   # 16
    'q': [1, 0, 0, 0, 1],   # 17
    'r': [1, 0, 0, 1, 0],   # 18
    's': [1, 0, 0, 1, 1],   # 19
    't': [1, 0, 1, 0, 0],   # 20
    'u': [1, 0, 1, 0, 1],   # 21
    'v': [1, 0, 1, 1, 0],   # 22
    'w': [1, 0, 1, 1, 1],   # 23
    'x': [1, 1, 0, 0, 0],   # 24
    'y': [1, 1, 0, 0, 1],   # 25
    'z': [1, 1, 0, 1, 0],   # 26
    '_': [1, 1, 1, 1, 1],   # 31 EOL
}

alpha_dec = [
    ' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
    'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
    'x', 'y', 'z', '0', '0', '0', '0', '_'
]


dataset = [
    # "a normal working day_",
    # "bring me that knife_",
    # "cats can see in the dark_",
    # "do is an irregular verb_",
    # "eventually this practice will catch up with us_",
    # "feel free to help yourself to coffee_",
    # "grab your coat and follow me_",
    # "have a nice day_",
    # "i always like to leave my desk clear at the end of the day_",
    # "just then the lights went out_",
    # "k",
    # "l",
    # "m",
    # "n",
    # "o",
    # "p",
    # "q",
    # "r",
    "some people believe that dreams reveal important things about your subconscious thoughts_",
    "the quick brown fox jumps over the lazy dog_",
    # "u",
    # "v",
    # "we went to edinburgh and back again all in one day_",
    # "x",
    # "y",
    # "z",
]


def float_to_bin(value):
    if value > 0.5:
        return 1
    return 0


def float_to_binary_array(float_array):
    bin_array = []
    for i in float_array:
        bin_array.append([float_to_bin(a) for a in i])
    return bin_array


def bin_arr_to_integer(arr):
    keys = [16, 8, 4, 2, 1]
    ret_val = 0
    for i in range(len(arr)):
        if arr[i] == 1:
            ret_val += keys[i]
    return ret_val


def binary_array_to_string(arr):
    ret_str = ""
    for a in arr:
        ret_str += alpha_dec[bin_arr_to_integer(a)]
    return ret_str


def string_to_binary_array(i_str):
    ret_val = []
    for i in i_str:
        ret_val.append(alphabet[i])
    return ret_val


def save_arch_to_file(network_arch, filename):
    with open(filename, 'w') as f:
        f.write(f"num_inputs: {network_arch['num_inputs']},\n")
        f.write(f"neurons: [\n")
        for n in network_arch['neurons']:
            f.write(f"\t{n},\n")
        f.write(f"],\n")
        f.write(f"output_indices: {network_arch['output_indices']}\n")


def get_net_arch(arch):
    # example_arch = {
    #     'direct': [{'idx': 16, 'type': 0, 'input_indices': [0, 1, 2, 3, 4, 5, 6, 7]},],
    #     'layers':[
    #         {"size": 16, "type": "input", "inputs": None},
    #         {"size": 16*16, "type": "hidden", "inputs": [0, 3]},
    #         {"size": 16*16, "type": "hidden", "inputs": [1]},
    #         {"size": 16*16, "type": "output", "inputs": [2]},
    #     ]
    # }
    # arch = example_arch
    arch_layers = arch['layers']
    net_arch = {
        "num_inputs": 0,
        "neurons": [],
        "output_indices": []
    }
    # Calculate indices
    indices = []
    idx = 0
    for layer in arch_layers:
        indices.append([i+idx for i in range(layer["size"])])
        idx += layer["size"]
        if layer["type"] == "output":
            net_arch['output_indices'].extend(indices[-1])
    # Calculate inputs indices
    inputs = []
    for i in range(len(arch_layers)):
        if arch_layers[i]["inputs"] is None:
            inputs.append([])
        else:
            temp = []
            for a in arch_layers[i]["inputs"]:
                temp.extend(indices[a])
            inputs.append(temp)

    for i in range(len(arch_layers)):
        if arch_layers[i]["type"] == "input":
            net_arch['num_inputs'] += arch_layers[i]["size"]
        else:
            for a in range(arch_layers[i]["size"]):
                net_arch['neurons'].append(
                    {"idx": indices[i][a], "type": int(NeuronTypes.Linear), "input_indices": inputs[i]}
                )
    return net_arch


def net_get_output(encoder, decoder, v_in, to_print=False):
    encoder_output_width = encoded_width
    decoder_output_width = 5+encoded_width

    encoder_inputs = []
    encoder_outputs = []
    for symbol in v_in:
        if len(encoder_outputs) == 0:
            e_input = symbol + [0 for _ in range(encoder_output_width)]
        else:
            e_input = symbol + encoder_outputs[-1]
        encoder_inputs.append(e_input)
        encoder_outputs.append(encoder.get_outputs(e_input, encoder_output_width))

    v_irt = encoder_outputs[-1] # Encoded vector

    v_out = []
    decoder_inputs = []
    decoder_outputs = []
    for _ in range(len(v_in)):
        if len(decoder_outputs) == 0:
            d_input = v_irt + [0 for _ in range(encoded_width)]
        else:
            d_input = v_irt + decoder_outputs[-1][5:]
        decoder_inputs.append(d_input)
        decoder_outputs.append(decoder.get_outputs(d_input, decoder_output_width))
        v_out.append(decoder_outputs[-1][:5])

    if to_print:
        print("encoder_inputs = ")
        for i in range(len(v_in)):
            print("\t[",  ", ".join([f"{a:.2f}" for a in encoder_inputs[i]]), "]")
        print("encoder_outputs = ")
        for i in range(len(v_in)):
            print("\t[",  ", ".join([f"{a:.2f}" for a in encoder_outputs[i]]), "]")
        print("decoder_inputs = ")
        for i in range(len(v_in)):
            print("\t[",  ", ".join([f"{a:.2f}" for a in decoder_inputs[i]]), "]")
        print("decoder_outputs = ")
        for i in range(len(v_in)):
            print("\t[",  ", ".join([f"{a:.2f}" for a in decoder_outputs[i]]), "]")
        print("v_in = ")
        for i in range(len(v_in)):
            print("\t[",  ", ".join([f"{a:.2f}" for a in v_in[i]]), "]")
        print("v_out = ")
        for i in range(len(v_in)):
            print("\t[",  ", ".join([f"{a:.2f}" for a in v_out[i]]), "]")
        # raise Exception("lalala")
    return v_out, encoder_inputs, encoder_outputs, decoder_inputs, decoder_outputs


def get_net_error(encoder, decoder, dataset, input_len, to_print=False):
    error_counter = 0
    error = 0
    max_error = 0
    for i in range(input_len):
        for s in dataset:
            # i_string = get_first_n_words(s, input_len)
            i_string = s[:i+1]
            v_in = string_to_binary_array(i_string)
            v_out = net_get_output(encoder, decoder, v_in, to_print)[0]
            e = get_network_error(v_in, v_out)
            error += e
            error_counter += 1
    return error/error_counter


def network_backprop(encoder, decoder, dataset, input_len):
    encoder_output_width = 4
    decoder_output_width = 5+4
    error_counter = 0
    error = 0
    h = 0.1
    
    for i in range(input_len):
        for s in dataset:
            # i_string = get_first_n_words(s, 1)
            i_string = s[:i+1]
            v_in = (string_to_binary_array(i_string))
            # v_in.append([0 for _ in range(16)]) # Add a zero-symbol at the end
            v_out, encoder_inputs, encoder_outputs, decoder_inputs, decoder_outputs = net_get_output(encoder, decoder, v_in)
            # encoder.clean()
            # decoder.clean()
            error += get_network_error(v_in, v_out)
            error_counter += 1
            # Reverse lists:
            encoder_inputs.reverse()
            encoder_outputs.reverse()
            decoder_inputs.reverse()
            decoder_outputs.reverse()

            ind_errors = [get_network_individual_errors(v_in[i], v_out[i]) for i in range(len(v_in))]
            ind_errors.reverse()

            # Update decoder:
            encoder_output_errors = []
            decoder_input_errors = [[0 for _ in range(5)]]
            for i in range(len(decoder_outputs)):
                decoder.get_outputs(decoder_inputs[i], decoder_output_width)
                individual_errors = ind_errors[i] + decoder_input_errors[-1]
                decoder.backpropagation(individual_errors)
                input_errors = decoder.get_input_errors(5+4)
                encoder_output_errors.append(input_errors[:4])
                decoder_input_errors.append(input_errors[4:])
            decoder.backprop_update_weights(h)
            # Calculate errors for the encoder:
            individual_errors = []    # Result is a 1-D array of errors, len == 256
            for i in range(len(encoder_output_errors[0])):
                err = 0
                for j in range(len(encoder_output_errors)):
                    err += encoder_output_errors[j][i]
                individual_errors.append(err/len(encoder_output_errors[0]))
            # Update encoder:
            for i in range(len(encoder_inputs)):
                encoder.get_outputs(encoder_inputs[i], encoder_output_width)
                encoder.backpropagation(individual_errors)
                individual_errors = encoder.get_input_errors(4+5)[4:] # Exclude errors of the symbol
            encoder.backprop_update_weights(h)
            # encoder.clean()
            # decoder.clean()

    return error/error_counter


class TestClassName(unittest.TestCase):

    def test_evolution(self):
        encoder_arch = get_net_arch([
            {"size": 5, "type": "input",  "inputs": None},
            {"size": encoded_width, "type": "input",  "inputs": None},
            {"size": 8,  "type": "hidden", "inputs": [0]},
            {"size": 8,  "type": "hidden", "inputs": [1]},
            {"size": 8,  "type": "hidden", "inputs": [2, 3]},
            {"size": encoded_width,  "type": "output", "inputs": [4]},
        ])
        decoder_arch = get_net_arch([
            {"size": encoded_width, "type": "input",  "inputs": None},
            {"size": encoded_width, "type": "input",  "inputs": None},
            {"size": 8,   "type": "hidden", "inputs": [0]},
            {"size": 8,   "type": "hidden", "inputs": [1]},
            {"size": 8,   "type": "hidden", "inputs": [2, 3]},
            {"size": 5+encoded_width,   "type": "output", "inputs": [4]},
        ])
        # save_arch_to_file(encoder_arch, "encoder_arch.txt")
        # save_arch_to_file(decoder_arch, "decoder_arch.txt")
        rng_seed = 1751501246

        dll_loader = LoaderIface()
        encoder = NetworkInterface(get_network_arch(**encoder_arch), dll_loader, rng_seed)
        decoder = NetworkInterface(get_network_arch(**decoder_arch), dll_loader, rng_seed)
        encoder.network_restore_coeffs("mini_encoder_coeffs.txt")
        decoder.network_restore_coeffs("mini_decoder_coeffs.txt")
        nets = [encoder, decoder]
        input_len = 8
        min_error = get_net_error(encoder, decoder, dataset, input_len, True)
        selector = 0
        print(f"Initial error: {min_error}")
        for lap in range(800):
            for _ in range(100000):
                if min_error < 0.0001:
                    # input_len += 1
                    break
                nets[selector].mutate(0.1)
                new_error = get_net_error(encoder, decoder, dataset, input_len)
                if new_error > min_error:
                    nets[selector].rollback()
                elif new_error < min_error:
                    min_error = new_error
                    print(f"\t{min_error = }, {input_len = }")
                if selector == 0:
                    selector = 1
                else:
                    selector = 0

            min_error = get_net_error(encoder, decoder, dataset, input_len, True)
            for d in dataset:
                i_string = d[:input_len]
                outputs = net_get_output(encoder, decoder, string_to_binary_array(i_string))[0]
                out_str = binary_array_to_string(float_to_binary_array(outputs))
                print(f"\tInput string: {i_string}; output string: {out_str}", flush=True)
            if min_error < 0.0001:
                print(f"\tFinal error: {min_error}")
                break
            encoder.network_save_coeffs("mini_encoder_coeffs.txt")
            decoder.network_save_coeffs("mini_decoder_coeffs.txt")

        print(f"\tFinal error: {min_error}")

        self.assertLess(1, 2)


if __name__ == "__main__":
    minicolumn_arch = get_net_arch([
        {"size": 25, "type": "input",  "inputs": None},        # Layer 4 inputs
        {"size": 25, "type": "hidden", "inputs": [0]},         # Layer 4 hidden

        {"size": 25, "type": "input",  "inputs": None},        # Layer 2/3 inputs
        {"size": 25, "type": "hidden", "inputs": [1, 2]},      # Layer 2/3 hidden
        {"size": 25, "type": "hidden", "inputs": [3]},         # Layer 2/3 outputs

        {"size": 25, "type": "hidden", "inputs": [4, 1]},      # Layer 5 hidden
        {"size": 25, "type": "hidden", "inputs": [5]},         # Layer 5 outputs

        {"size": 25, "type": "output", "inputs": [6]},         # Layer 6 outputs
    ])
    unittest.main()
