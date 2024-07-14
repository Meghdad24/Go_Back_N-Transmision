import socket
import sys
import threading
import time

from helper import mod2div, Go_back_n_codeword

CODEWORD_SIZE = 20
DATA_SIZE = 14
PATTERN_SIZE = CODEWORD_SIZE - DATA_SIZE + 1

codeword_list = []


def init_data():
    global codeword_list
    data_values = [
        "01100000110100", "01010111001001", "10010101100101", "00101010110011",
        "11110100111000", "00000111010111", "01100000110100", "01010111001001",
        "10010101100101", "00101010110011", "11110100111000", "00000111010111",
        "01010111111001", "00000011111011", "11110111110001", "01110101001011"
    ]
    codeword_list = [Go_back_n_codeword(data, "".zfill(CODEWORD_SIZE - DATA_SIZE), idx) for idx, data in
                 enumerate(data_values)]


init_data()

# pattern = generate_binary_string(PATTERN_SIZE)
# print(f"Generated Pattern: {pattern}")
pattern = "1101011"

def FCS_generator(data: str, p: str):
    data = data.ljust(CODEWORD_SIZE, '0')
    fcs = mod2div(data, p)
    fcs = fcs.zfill(CODEWORD_SIZE - DATA_SIZE)
    return fcs


for codeword in codeword_list:
    codeword.set_fcs(FCS_generator(codeword.data, pattern))
    print(str(codeword))

# test CRC
for codeword in codeword_list:
    print(mod2div(codeword.get_codeword(), pattern))











HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65431  # The port used by the server

GO_BACK_N_WINDOW_SIZE = 5
FREE_SLOT = GO_BACK_N_WINDOW_SIZE
TIMEOUT = 10

RUNNING = True

send_index = 0
next_index_ACK = 0

def response_recv(s):
    global FREE_SLOT, next_index_ACK, RUNNING, send_index

    while RUNNING:
        try:
            time.sleep(1)
            response = s.recv(1024).decode('utf-8')
            if response == f"ACK{next_index_ACK}":
                FREE_SLOT += 1
                next_index_ACK += 1
                print(f"Received: {response}")
            elif "REJ" in response:  # error detected by CRC
                print(f"Received REJ{response[3:]}!")
                FREE_SLOT = GO_BACK_N_WINDOW_SIZE
                send_index = int(response[3:])
            elif "TO" in response:  # timeout server recv
                print(f"Received TO{response[2:]}!")
                FREE_SLOT = GO_BACK_N_WINDOW_SIZE
                send_index = int(response[2:])
            elif "OO" in response:  # out of order data received by server
                print(f"Received OO{response[2:]}!")
                FREE_SLOT = GO_BACK_N_WINDOW_SIZE
                send_index = int(response[2:])
        except socket.error as exception:
            print(f"Socket error: {exception}")
            RUNNING = False


def shutdown(ack_recv_t, er: int):
    global RUNNING, sock
    RUNNING = False
    ack_recv_t.join()
    sock.close()
    print("Shut down!")
    sys.exit(er)
    pass


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((HOST, PORT))
ack_recv_t = threading.Thread(target=response_recv, args=(sock,))
ack_recv_t.start()


while next_index_ACK != (len(codeword_list) - 1):
    while send_index < len(codeword_list):
        if FREE_SLOT > 0:
            time.sleep(0.5)
            sock.sendall(str(codeword_list[send_index]).encode("utf-8"))
            print(
                f"{codeword_list[send_index].data}{codeword_list[send_index].fcs} with index {send_index} sent.")
            send_index += 1
            FREE_SLOT -= 1
        else:
            while FREE_SLOT < 1:
                time.sleep(1)
    pass

shutdown(ack_recv_t, 1)
print("END")
