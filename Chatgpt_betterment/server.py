import socket
import threading
import time
import queue

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65431  # Port to listen on (non-privileged ports are > 1023)

RUNNING = True

Buffer = queue.Queue()


def ack_send():
    global Buffer
    while RUNNING:
        time.sleep(3)
        if not Buffer.empty():
            data = Buffer.get()
            conn.sendall(("ACK" + data[14:]).encode("utf-8"))
            print(f"send {data[14:]}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    ack_send = threading.Thread(target=ack_send)
    ack_send.start()

    print("waiting for a connection...")
    conn, client_addr = s.accept()
    with conn:
        print(f"Connected by {client_addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data = data.decode("utf-8")
            Buffer.put(data)
            print(data)

    RUNNING = False
    ack_send.join()

