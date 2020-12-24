import socket
import select

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#to overcome address already in use error
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

#making a list of sockets for select to keep track of
sockets_list = [server_socket]
#it will save client's username and its size
clients = {}

print(f'Listening for connections on {IP}:{PORT}')


#handles receiving messages
def receive_message(client_socket):
    try:
        #1st receiving only the header
        message_header = client_socket.recv(HEADER_LENGTH)  #it'll be received in bytes
        if not len(message_header):     #if client closed 'gracefully' and didnt give anything
            return False
        message_length = int(message_header.decode('utf-8').strip())    #strip just to handle if whitespace not stripped, tho in python it automatically strips

        return {'header':message_header, 'data':client_socket.recv(message_length)}

    except: #if something went wrong like empty msg or client closed connection
        return False




# Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    #read_sockets will have server_socket if there is a new connection
    #else it will have a client_socket if the connected client socket wants to send a msg
    ##this is because select.select() returns a subset of the 1st 3 args
    ##so in sockets_list, first we have the server_socket, then we append a client_socket to it below
    ###########################################

    #now iterating over read_sockets, which have some data to be read
    for notified_socket in read_sockets:
        if notified_socket == server_socket:    #means we have a new connection
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)   #user is a dict having header and data, name is user cuz at starting, client send username

            #if for some reason client close connection, we just move along(continuing for loop)
            if user is False:
                continue

            sockets_list.append(client_socket)
            #in clients dict, we stored user with key as the client socket object (not just its name, but whole obj)
            clients[client_socket] = user

            #first thing that client will send will be a username in the data field in user dict
            print('Accepted new connection from {}:{}, Username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:   #notified socket not a server socket, so we have a new msg to read
            message = receive_message(notified_socket)  #notified_socket is a client_socket now
            #Before we attempt to read the message, let's make sure one exists. 
            #If the client disconnects, then the message would be empty:
            if message is False:
                print('Closed connection from {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                #continuing the for loop of notified socket
                continue
            
            #if it was not a disconnect
            user = clients[notified_socket]
            print('Received message from {}:'.format(user['data'].decode('utf-8')))
            print(message['data'].decode('utf-8'))


            #now sending this received msg to all clients
            for client_socket in clients:

                #not sending the message to sender-----------
                if client_socket is not notified_socket:    # != written in tutorial
                    #sending both username and the message
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            
    # It's not really necessary to have this, but will handle some socket exceptions just in case
    ##??
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
            sockets_list.remove(notified_socket)
            # Remove from our list of users
            del clients[notified_socket]
