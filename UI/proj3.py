import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import time
import queue
from helper import generate_binary_string, Go_back_n_data

# Server and Client configurations
HOST = "127.0.0.1"
PORT = 65431

# Global variables for server
RUNNING_SERVER = True
Buffer = queue.Queue()

# Global variables for client
RUNNING_CLIENT = True
data_list = []
GO_BACK_N_WINDOW_SIZE = 5
FREE_SLOT = 4
CODEWORD_SIZE = 20
DATA_SIZE = 14
Pattern = generate_binary_string(CODEWORD_SIZE - DATA_SIZE + 1)

# Server functions
def start_server():
    global RUNNING_SERVER
    RUNNING_SERVER = True
    threading.Thread(target=server_thread).start()

def stop_server():
    global RUNNING_SERVER
    RUNNING_SERVER = False
    server_log.insert(tk.END, "Server stopped.\n")

def server_thread():
    global Buffer
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        threading.Thread(target=ack_send).start()

        server_log.insert(tk.END, "Waiting for a connection...\n")
        conn, client_addr = s.accept()
        with conn:
            server_log.insert(tk.END, f"Connected by {client_addr}\n")
            while RUNNING_SERVER:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode("utf-8")
                Buffer.put(data)
                server_log.insert(tk.END, f"Received: {data}\n")

        while not Buffer.empty():
            pass

def ack_send():
    global Buffer
    while RUNNING_SERVER:
        time.sleep(5)
        if not Buffer.empty():
            data = Buffer.get()
            conn.sendall(("ACK" + data[14:]).encode("utf-8"))
            server_log.insert(tk.END, f"Sent ACK for: {data[14:]}\n")

# Client functions
def start_client():
    adding_data()
    threading.Thread(target=client_thread).start()

def stop_client():
    global RUNNING_CLIENT
    RUNNING_CLIENT = False
    client_log.insert(tk.END, "Client stopped.\n")

def adding_data():
    global data_list
    data_list = [
        Go_back_n_data("01100000110100", 0),
        Go_back_n_data("01010111001001", 1),
        Go_back_n_data("10010101100101", 2),
        Go_back_n_data("00101010110011", 3),
        Go_back_n_data("11110100111000", 4),
        Go_back_n_data("00000111010111", 5),
        Go_back_n_data("01100000110100", 6),
        Go_back_n_data("01010111001001", 7),
        Go_back_n_data("10010101100101", 8),
        Go_back_n_data("00101010110011", 9),
        Go_back_n_data("11110100111000", 10),
        Go_back_n_data("00000111010111", 11)
    ]

def client_thread():
    global FREE_SLOT, next_index
    next_index = 0
    timeout = 10

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        threading.Thread(target=ack_recv, args=(s,)).start()

        i = 0
        while i < len(data_list):
            if FREE_SLOT > 0:
                s.sendall((str(data_list[i])).encode("utf-8"))
                client_log.insert(tk.END, f"Sent: {data_list[i].data} with index {data_list[i].index}\n")
                FREE_SLOT -= 1
                i += 1
            else:
                while FREE_SLOT < 1 and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                if timeout == 0:
                    client_log.insert(tk.END, "Timeout!\n")
                    sys.exit(0)
                else:
                    timeout = 10

        while next_index != len(data_list):
            pass

def ack_recv(s):
    global FREE_SLOT, next_index

    while RUNNING_CLIENT:
        response = s.recv(1024)
        client_log.insert(tk.END, f"Received: {response.decode('utf-8')}\n")

        if response.decode('utf-8') == ("ACK" + str(next_index)):
            FREE_SLOT += 1
            next_index += 1

# UI setup
app = tk.Tk()
app.title("Server & Client")

# Server UI
server_frame = tk.Frame(app)
server_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(server_frame, text="Server").pack()
start_server_button = tk.Button(server_frame, text="Start Server", command=start_server)
start_server_button.pack()
stop_server_button = tk.Button(server_frame, text="Stop Server", command=stop_server)
stop_server_button.pack()

server_log = scrolledtext.ScrolledText(server_frame, width=50, height=20)
server_log.pack()

# Client UI
client_frame = tk.Frame(app)
client_frame.pack(side=tk.RIGHT, padx=10, pady=10)

tk.Label(client_frame, text="Client").pack()
start_client_button = tk.Button(client_frame, text="Start Client", command=start_client)
start_client_button.pack()
stop_client_button = tk.Button(client_frame, text="Stop Client", command=stop_client)
stop_client_button.pack()

client_log = scrolledtext.ScrolledText(client_frame, width=50, height=20)
client_log.pack()

app.mainloop()
