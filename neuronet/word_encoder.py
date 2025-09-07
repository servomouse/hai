import random

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
    print(top_vals)
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

def average_error(initial, result):
    total_error = 0
    count = 0

    for init_val, res_val in zip(initial, result):
        if res_val != 0:
            total_error += average_error_ind(init_val, res_val)
            count += 1

    average = total_error / count if count > 0 else 0
    return average

def distribution_error(result_arrays, target_usage):
    length = len(result_arrays[0])
    usage_count = [0] * length

    for result in result_arrays:
        for index, value in enumerate(result):
            if value != 0:
                usage_count[index] += 1

    total_error = sum(abs(count - target_usage) for count in usage_count)
    average_error = total_error / length if length > 0 else 0

    return average_error


init_arrs = [get_init_arr(12) for _ in range(20)]
sparse_arrs = []
for a in init_arrs:
    print(a)
    sparse_arrs.append(sparsify(5, a))
for a in sparse_arrs:
    print(a)

print(average_error(init_arrs, sparse_arrs))
print(distribution_error(sparse_arrs, 5))