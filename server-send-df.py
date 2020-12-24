import socket
import pandas as pd 
import pickle


HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1235

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

while True:
    server_socket.listen()
    client_socket, address = server_socket.accept()

    df = pd.read_csv('Demo_db.csv')
    msg = pickle.dumps(df)
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", 'utf-8') + msg

    print(f"Connection from {address} has been established, sending it the dataframe")
    client_socket.sendall(msg)
    client_socket.close()

