import random
from config import alphabet
from dataset import english_words
import math
import sys, os

from word_encoder import sparse_encode_word, load_encoder

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, get_net_arch, save_arch_to_file, NeuronTypes
from python.dll_loader import LoaderIface

ENCODED_WIDTH = 32
LETTER_WIDTH = 5
SPARSE_PARAM = 5


def word_representation(word):
    output = []
    for letter in word:
        output.append(alphabet[letter])
    output.append(alphabet['EOL'])
    return output


def get_vector_error(output_vec, target_vec):
    error = 0
    for i in range(len(output_vec)):
        error += abs(output_vec[i] - target_vec[i])
    return error / len(output_vec)


def get_decoder_error(decoder:NetworkInterface, dataset, to_print=False):
    error = 0
    for d in dataset:
        input_vector = d[0]
        outputs = d[1]
        curr_output = [0 for _ in range(LETTER_WIDTH)] + [input_vector[i] for i in range(ENCODED_WIDTH)]
        local_error = 0
        for i in range(len(outputs)):
            curr_output = decoder.get_outputs(curr_output[LETTER_WIDTH:], LETTER_WIDTH + ENCODED_WIDTH)
            local_error += get_vector_error(curr_output[:LETTER_WIDTH], outputs[i])
        error += local_error / len(outputs)
    return error / len(dataset)


def train_decoder(decoder, dataset):

    min_error = get_decoder_error(decoder, dataset, to_print=True)
    print(f"Initial error: {min_error}")
    for t in range(100):
        for lap in range(100):
            print(f"\r{t = }, {lap = }", end='')
            decoder.mutate(0.1)
            new_error = get_decoder_error(decoder, dataset)
            if new_error > min_error:
                decoder.rollback()
            elif new_error < min_error:
                min_error = new_error
                print(f", {min_error = }")

        decoder.network_save_coeffs("decoder_coeffs.txt")
    print(f"\tFinal error: {get_decoder_error(decoder, dataset, to_print=True)}")


def main():
    decoder_arch = get_net_arch([
        {"size": ENCODED_WIDTH, "type": "input",  "inputs": None},
        # {"size": ENCODED_WIDTH, "type": "input",  "inputs": None},
        {"size": 8,  "type": "hidden", "inputs": [0]},
        {"size": 8,  "type": "hidden", "inputs": [1]},
        {"size": 8,  "type": "hidden", "inputs": [2]},
        {"size": LETTER_WIDTH + ENCODED_WIDTH,  "type": "output", "inputs": [3]},
    ])
    # save_arch_to_file(decoder_arch, "decoder_arch.txt")

    dll_loader = LoaderIface()
    decoder = NetworkInterface(get_network_arch(**decoder_arch), dll_loader)
    decoder.network_restore_coeffs("decoder_coeffs.txt")

    encoder = load_encoder()

    dataset = [[sparse_encode_word(encoder, w), word_representation(w), w] for w in random.sample(english_words, 10000)]

    # for d in dataset:
    #     print(d[0])
    #     print(d[1])
    #     print(d[2], "\n")

    train_decoder(decoder, dataset)


if __name__ == "__main__":
    main()