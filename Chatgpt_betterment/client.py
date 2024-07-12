import socket
import threading
import time

from helper import generate_binary_string, Go_back_n_data

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65431  # The port used by the server

GO_BACK_N_WINDOW_SIZE = 5
FREE_SLOT = GO_BACK_N_WINDOW_SIZE

CODEWORD_SIZE = 20
DATA_SIZE = 14
PATTERN_SIZE = CODEWORD_SIZE - DATA_SIZE + 1

TIMEOUT = 10

RUNNING = True
data_list = []
next_index = 0


def init_data():
    global data_list

    data_values = [
        "01100000110100", "01010111001001", "10010101100101", "00101010110011",
        "11110100111000", "00000111010111", "01100000110100", "01010111001001",
        "10010101100101", "00101010110011", "11110100111000", "00000111010111"
    ]
    data_list = [Go_back_n_data(data, idx) for idx, data in enumerate(data_values)]


def ack_recv(s):
    global FREE_SLOT, next_index, RUNNING

    while RUNNING:
        try:

            response = s.recv(1024).decode('utf-8')
            if response == f"ACK{next_index}":
                FREE_SLOT += 1
                next_index += 1
                print(f"Received: {response}")

        except socket.error as exception:
            print(f"Socket error: {exception}")
            RUNNING = False


init_data()

pattern = generate_binary_string(CODEWORD_SIZE - DATA_SIZE + 1)
print(f"Generated Pattern: {pattern}")


def shutdown(ack_recv_t):
    global RUNNING
    RUNNING = False
    ack_recv_t.join()
    pass


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    try:
        sock.connect((HOST, PORT))
        ack_recv_t = threading.Thread(target=ack_recv, args=(sock,))
        ack_recv_t.start()

        send_index = 0
        i = 0
        while i < len(data_list):
            if FREE_SLOT > 0:
                sock.sendall(str(data_list[i]).encode("utf-8"))
                print(f"{data_list[i].data} with index {data_list[i].index} sent.")
                send_index += 1
                FREE_SLOT -= 1
                i += 1
            else:
                remaining_time = TIMEOUT
                while FREE_SLOT < 1 and remaining_time > 0:
                    time.sleep(1)
                    remaining_time -= 1
                if remaining_time == 0:
                    print("Timeout!")
                    shutdown(ack_recv_t)

        while next_index != len(data_list):
            pass

    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        shutdown(ack_recv_t)
