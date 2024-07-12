import random
import time


def generate_binary_string(n):
    number = random.getrandbits(n)
    binary_string = format(number, '0b').zfill(n)
    return binary_string


class Go_back_n_data:

    def __init__(self, data, index):
        self.data = data
        self.index = index

    def __str__(self):
        return f"{self.data}{self.index}"

# Optional: You can add more helper functions or classes here if needed.
