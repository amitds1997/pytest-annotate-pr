from functions.basic_functions import add_numbers, multiply_numbers


def test_add_numbers():
    return add_numbers(4, 3) == 7


def test_multiply_numbers():
    return multiply_numbers(3, 5) == 15