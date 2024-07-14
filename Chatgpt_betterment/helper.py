import random

class Go_back_n_codeword:

    def __init__(self, data, fcs, index):
        self.data = data
        self.fcs = fcs
        self.index = index

    def set_fcs(self,fcs):
        self.fcs = fcs

    def get_codeword(self):
        return f"{self.data}{self.fcs}"

    def __str__(self):
        return f"{self.data}{self.fcs},{self.index}"


def xor(a, b):
    result = []
    for i in range(1, len(b)):
        if a[i] == b[i]:
            result.append('0')
        else:
            result.append('1')
    return ''.join(result)


def mod2div(data: str, p: str):
    pick = len(p)
    tmp = data[0:pick]
    while pick < len(data):
        if tmp[0] == '1':
            tmp = xor(p, tmp) + data[pick]
        else:
            tmp = xor('0' * pick, tmp) + data[pick]
        pick += 1

    if tmp[0] == '1':
        tmp = xor(p, tmp)
    else:
        tmp = xor('0' * pick, tmp)

    return tmp
