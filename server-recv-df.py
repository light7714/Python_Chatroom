import socket
import pandas as pd 
import pickle

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1236

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#to overcome address already in use error
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

while True:
    server_socket.listen()
    client_socket, address = server_socket.accept()

    message_header = client_socket.recv(HEADER_LENGTH)
    if not len(message_header):
        error_callback('Connection closed by the server, could not retrieve data')
    
    message_length = int(message_header.decode('utf-8').strip())
    message = client_socket.recv(message_length)

    df = pickle.loads(message)

    df.to_csv('Demo_db.csv', index=False)
    client_socket.close()