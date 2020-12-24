# import socket
# import pandas as pd 
# import pickle

# HEADER_LENGTH = 10
# ip = '0.tcp.ap.ngrok.io'
# port = 14466

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect((ip, port))

# message_header = client.recv(HEADER_LENGTH)
# #print(message_header)
# if not message_header:
#     print('error')

# message_length = int(message_header.decode('utf-8').strip())
# message = client.recv(message_length)

# df = pickle.loads(message)
# print(df)
import pandas as pd 
df = pd.read_csv('Demo_db.csv')
print(df)