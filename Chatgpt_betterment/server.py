import socket
import threading
import time
import queue
from helper import mod2div

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65431  # Port to listen on (non-privileged ports are > 1023)

CODEWORD_SIZE = 20
current_codeword_SIZE = 14
PATTERN_SIZE = CODEWORD_SIZE - current_codeword_SIZE + 1

RUNNING = True
TIMEOUT = 5

Buffer = queue.Queue()

next_index = 0

pattern = "1101011"


def response_send():
    global Buffer, next_index
    # CRC & TimeOUT error simulation
    error_index = 5
    timeout = TIMEOUT
    while RUNNING:
        time.sleep(2)
        if not Buffer.empty():
            current_codeword = Buffer.get().split(",")

        # CRC error simulation:
            # if int(current_codeword[1]) == error_index:
            #     current_codeword[0] = "01011101100001010010"
            #     error_index += 3

            if int(current_codeword[1]) != next_index:
                conn.sendall(("OO" + str(next_index)).encode("utf-8")) # Out of order!
                print(f"OO -> ERROR {current_codeword[1]}")
                Buffer = queue.Queue()
                timeout = TIMEOUT
            else:
                if error_detection_crc(current_codeword[0]):
                    conn.sendall(("REJ" + current_codeword[1]).encode("utf-8"))
                    print(f"REJ -> ERROR {current_codeword[1]}")
                    Buffer = queue.Queue()
                    timeout = TIMEOUT
                else:
                    conn.sendall(("ACK" + current_codeword[1]).encode("utf-8"))
                    print(f"ACK send {current_codeword[1]}")
                    next_index += 1
                    timeout = TIMEOUT
        else:
            time.sleep(1000)
            timeout -= 1
            print(f"SEND time remaining: {timeout}")
            pass

    print("thread exit")

def error_detection_crc(codeword) -> bool:
    if int(mod2div(codeword, pattern), 2) == 0:
        return False
    return True

def shutdown(ack_send_t):
    global RUNNING, sock
    RUNNING = False
    ack_send_t.join()
    sock.close()
    print("Shut down!")
    pass

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()

ack_send_t = threading.Thread(target=response_send)
ack_send_t.start()

print("waiting for a connection...")
conn, client_addr = sock.accept()

# OUT of ORDER & TimeOUT error simulation
# error_index = 5
# timeout = TIMEOUT

with conn:
    print(f"Connected by {client_addr}")
    while True:
        current_codeword = conn.recv(1024)
        if not current_codeword:
            break
        current_codeword = current_codeword.decode("utf-8")
        Buffer.put(current_codeword)
        print(f"{current_codeword} (Buffer)")
        last_index_recv = int(current_codeword.split(",")[1])

    # OUT of ORDER error simulation:

        # if int(current_codeword.split(",")[1]) != error_index:
        #     Buffer.put(current_codeword)
        #     print(f"{current_codeword} (Buffer)")
        # else:
        #     error_index += 3

    # TimeOut error simulation:

        # if error_index != 0:
        #     current_codeword = conn.recv(1024)
        #     if not current_codeword:
        #         break
        #     error_index -= 1
        #     current_codeword = current_codeword.decode("utf-8")
        #     Buffer.put(current_codeword)
        #     print(f"{current_codeword} (Buffer)")
        #     last_index_recv = int(current_codeword.split(",")[1])
        # else :
        #     time.sleep(1)
        #     timeout -= 1
        #     print(f"RECV time remaining: {timeout}s")
        #     if timeout <= 0:
        #         print(f"TimeOUT. expected for index {last_index_recv + 1}")
        #         while not Buffer.empty():
        #             pass
        #         conn.sendall(f"TO{last_index_recv + 1}".encode("utf-8"))
        #         timeout = TIMEOUT
        #         error_index = 5
        #         conn.recv(1024)

    print("exit")


shutdown(ack_send_t)
print("END")
