import random
def bubble_sort(arr):
    """冒泡排序"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def selection_sort(arr):
    """选择排序"""
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def insertion_sort(arr):
    """插入排序"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

# 测试代码
numbers = [64, 34, 25, 12, 22, 11, 90, 88, 45, 73]

print("原始数组:", numbers)

# 测试冒泡排序
bubble_result = bubble_sort(numbers.copy())
print("冒泡排序结果:", bubble_result)

# 测试选择排序
selection_result = selection_sort(numbers.copy())
print("选择排序结果:", selection_result)

# 测试插入排序
insertion_result = insertion_sort(numbers.copy())
print("插入排序结果:", insertion_result)