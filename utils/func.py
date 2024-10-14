
def sum_list(arr, n):
    temp = [0 for _ in range(len(arr))]
    for i in range(len(arr)):
        if i == 0:
            temp[i] = arr[i]
        else:
            temp[i] = arr[i] + temp[i-1]
    for i in range(len(temp)):
        temp[i] = temp[i]/n
    return temp