import random
from config import alphabet
from dataset import english_words
import math
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.interface import NetworkInterface, get_network_error, get_network_individual_errors
from python.network import get_network_arch, get_net_arch, save_arch_to_file, NeuronTypes
from python.dll_loader import LoaderIface

ENCODED_WIDTH = 32
LETTER_WIDTH = 5
SPARSE_PARAM = 5


def get_init_arr(arr_len):
    return [round(1 - (2 * random.random()), 2) for _ in range(arr_len)]


def shift_arr(idx, arr):
    for i in range(len(arr)-1, idx, -1):
        arr[i] = arr[i-1]
    return arr


def sparsify(n, arr):
    top_vals = [[0, 0] for _ in range(n)]
    for i in range(len(arr)):
        vabs = abs(arr[i])
        for j in range(n):
            if vabs > top_vals[j][0]:
                top_vals = shift_arr(j, top_vals)
                top_vals[j] = [vabs, i]
                break
    # print(top_vals)
    sparse_arr = [0 for _ in range(len(arr))]
    for v in top_vals:
        idx = v[1]
        if arr[idx] > 0:
            sparse_arr[idx] = 1
        else:
            sparse_arr[idx] = -1
    return sparse_arr


def average_error_ind(initial, result):
    total_error = 0
    count = 0

    for init_val, res_val in zip(initial, result):
        if res_val != 0:
            error = abs(init_val - res_val)
            total_error += error
            count += 1

    average = total_error / count if count > 0 else 0
    return average


def delta_error(initial, result):
    # Average of how each non-zero element differs from its ideal value (-1 or 1)
    total_error = 0
    count = 0

    for init_val, res_val in zip(initial, result):
        if res_val != 0:
            total_error += average_error_ind(init_val, res_val)
            count += 1

    average = total_error / count if count > 0 else 0
    return average


def distribution_error(result_arrays):
    # How element usage differs from the ideal value
    arr_length = len(result_arrays[0])
    usage_count = [0] * arr_length
    counter = 0

    for result in result_arrays:
        for index, value in enumerate(result):
            if value != 0:
                usage_count[index] += 1
                counter += 1
    
    target_item_usage = counter/arr_length
    gran_error = [abs((count/target_item_usage) - 1) for count in usage_count]
    average_error = sum(gran_error) / len(gran_error)

    return average_error


def has_duplicates(array_of_arrays):
    # Convert each inner array to a tuple (which is hashable) and store in a set
    seen = set()
    for inner_array in array_of_arrays:
        # Convert inner array to a tuple
        tuple_inner = tuple(inner_array)
        # Check if the tuple is already in the set
        if tuple_inner in seen:
            return False  # Duplicate found
        seen.add(tuple_inner)
    return True  # No duplicates found


def get_encoder_error(encoder, words, to_print=False):
    dense_outputs = []
    sparse_outputs = []
    for word in words:
        dense_output = encode_word(encoder, word)
        sparse_output = sparsify(SPARSE_PARAM, dense_output)
        dense_outputs.append(dense_output)
        sparse_outputs.append(sparse_output)
        # if to_print:
        #     print(f"{sparse_output = }, {word = }")
        #     # print(f"{dense_output = }")
        #     # print(f"{sparse_output = }")
        #     # print("==================================")
    
    delta = delta_error(dense_outputs, sparse_outputs)
    distr = distribution_error(sparse_outputs)
    # if to_print:
    #     print(f"{delta = }")
    #     print(f"{distr = }")
    total_error = math.sqrt(delta**2 + distr**2)
    return total_error, has_duplicates(sparse_outputs)


def encode_word(encoder, word):
    output = [0 for _ in range(ENCODED_WIDTH)]
    for letter in word:
        output = encoder.get_outputs(alphabet[letter] + output, ENCODED_WIDTH)
    output = encoder.get_outputs(alphabet['EOL'] + output, ENCODED_WIDTH)
    return output


def main():
    encoder_arch = get_net_arch([
        {"size": LETTER_WIDTH, "type": "input",  "inputs": None},
        {"size": ENCODED_WIDTH, "type": "input",  "inputs": None},
        {"size": 8,  "type": "hidden", "inputs": [0]},
        {"size": 8,  "type": "hidden", "inputs": [1]},
        {"size": 8,  "type": "hidden", "inputs": [2, 3]},
        {"size": ENCODED_WIDTH,  "type": "output", "inputs": [4]},
    ])
    save_arch_to_file(encoder_arch, "encoder_arch.txt")

    dll_loader = LoaderIface()
    encoder = NetworkInterface(get_network_arch(**encoder_arch), dll_loader)
    encoder.network_restore_coeffs("encoder_coeffs.txt")

    dataset = english_words

    min_error, _ = get_encoder_error(encoder, dataset, to_print=True)
    print(f"Initial error: {min_error}")
    no_duplicates = False
    for t in range(100):
        for lap in range(10000):
            print(f"\r{t = }, {lap = }", end='')
            if no_duplicates:
                break
            encoder.mutate(0.1)
            new_error, has_duplicates = get_encoder_error(encoder, dataset)
            if not has_duplicates:
                no_duplicates = True
            if new_error > min_error:
                encoder.rollback()
            elif new_error < min_error:
                min_error = new_error
                print(f", {min_error = }")
        if no_duplicates:
            break

        encoder.network_save_coeffs("encoder_coeffs.txt")
    print(f"\tFinal error: {get_encoder_error(encoder, dataset, to_print=True)}")


    # init_arrs = [get_init_arr(12) for _ in range(20)]
    # sparse_arrs = []
    # for a in init_arrs:
    #     # print(a)
    #     sparse_arrs.append(sparsify(5, a))
    # # for a in sparse_arrs:
    # #     print(a)

    # delta = delta_error(init_arrs, sparse_arrs)
    # distr = distribution_error(sparse_arrs)
    # total_error = math.sqrt(delta**2 + distr**2)
    # print(delta)
    # print(distr)
    # print(total_error)


if __name__ == "__main__":
    main()