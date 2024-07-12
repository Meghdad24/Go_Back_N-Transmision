
import socket
import sys
import time

from helper import generate_binary_string, Go_back_n_data
import threading

RUNNING = True

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65431  # The port used by the server

data_list = []

GO_BACK_N_WINDOW_SIZE = 5
FREE_SLOT = GO_BACK_N_WINDOW_SIZE

CODEWORD_SIZE = 20
DATA_SIZE = 14

Pattern = generate_binary_string(CODEWORD_SIZE - DATA_SIZE + 1)

print(Pattern)


def adding_data():
    data0 = Go_back_n_data("01100000110100", 0)
    data1 = Go_back_n_data("01010111001001", 1)
    data2 = Go_back_n_data("10010101100101", 2)
    data3 = Go_back_n_data("00101010110011", 3)
    data4 = Go_back_n_data("11110100111000", 4),
    data5 = Go_back_n_data("00000111010111", 5)
    data6 = Go_back_n_data("01100000110100", 6)
    data7 = Go_back_n_data("01010111001001", 7)
    data8 = Go_back_n_data("10010101100101", 8)
    data9 = Go_back_n_data("00101010110011", 9)
    data10 = Go_back_n_data("11110100111000", 10)
    data11 = Go_back_n_data("00000111010111", 11)
    data_list.append(data0)
    data_list.append(data1)
    data_list.append(data2)
    data_list.append(data3)
    data_list.append(data4)
    data_list.append(data5)
    data_list.append(data6)
    data_list.append(data7)
    data_list.append(data8)
    data_list.append(data9)
    data_list.append(data10)
    data_list.append(data11)


adding_data()

timeout = 10

next_index = 0


def ack_recv(s):
    global FREE_SLOT
    global next_index

    while RUNNING:
        response = s.recv(1024)
        print(response)

        if response.decode('utf-8') == ("ACK" + str(next_index)):
            FREE_SLOT += 1
            next_index += 1
            print(response)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    threading.Thread(target=ack_recv, args=(s,)).start()

    send_index = 0

    i = 0
    while i < len(data_list):
        if FREE_SLOT > 0:
            time.sleep(2)
            s.sendall((str(data_list[i])).encode("utf-8"))
            print(data_list[i].data + " with index " + str(data_list[i].index) + " sended.")
            send_index += 1
            FREE_SLOT -= 1
            i += 1
            # response = s.recv(1024)
        else:
            while FREE_SLOT < 1 and timeout > 0:
                time.sleep(1)
                timeout -= 1
            if timeout == 0:
                # send_index = next_index
                print("time out!")
                sys.exit(0)
            else:
                timeout = 10

    while next_index != len(data_list):
        pass

    RUNNING = False

