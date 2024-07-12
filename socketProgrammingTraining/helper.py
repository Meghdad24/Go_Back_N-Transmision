import random

def generate_binary_string(n):
    # Generate a random number with n bits
    number = random.getrandbits(n)
    # Convert the number to binary
    binary_string = format(number, '0b')
    return binary_string

class Go_back_n_data:
    def __init__(self, data, index):
        self.data = data
        self.index = index

    def __str__(self):
        return f"{self.data}{self.index}"