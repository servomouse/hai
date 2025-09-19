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


def get_decoder_error(decoder, dataset, to_print=False):
    pass


def train_decoder(decoder, dataset):

    min_error, _ = get_decoder_error(decoder, dataset, to_print=True)
    print(f"Initial error: {min_error}")
    no_duplicates = False
    for t in range(100):
        for lap in range(10000):
            print(f"\r{t = }, {lap = }", end='')
            if no_duplicates:
                break
            decoder.mutate(0.1)
            new_error, has_duplicates = get_decoder_error(decoder, dataset)
            if not has_duplicates:
                no_duplicates = True
            if new_error > min_error:
                decoder.rollback()
            elif new_error < min_error:
                min_error = new_error
                print(f", {min_error = }")
        if no_duplicates:
            break

        decoder.network_save_coeffs("encoder_coeffs.txt")
    print(f"\tFinal error: {get_decoder_error(decoder, dataset, to_print=True)}")


def main():
    decoder_arch = get_net_arch([
        {"size": ENCODED_WIDTH, "type": "input",  "inputs": None},
        {"size": ENCODED_WIDTH, "type": "input",  "inputs": None},
        {"size": 8,  "type": "hidden", "inputs": [0]},
        {"size": 8,  "type": "hidden", "inputs": [1]},
        {"size": 8,  "type": "hidden", "inputs": [2, 3]},
        {"size": LETTER_WIDTH + ENCODED_WIDTH,  "type": "output", "inputs": [4]},
    ])
    # save_arch_to_file(decoder_arch, "decoder_arch.txt")

    dll_loader = LoaderIface()
    decoder = NetworkInterface(get_network_arch(**decoder_arch), dll_loader)
    # decoder.network_restore_coeffs("decoder_coeffs.txt")
    encoder = load_encoder()

    dataset = [[sparse_encode_word(encoder, w), w] for w in random.sample(english_words, 1000)]

    train_decoder(decoder, dataset)


if __name__ == "__main__":
    main()