import socket
import pickle
import struct
import pandas
from numpy import array

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 65400))
s.listen()

print("\n***Socket started, waiting for connection")
conn, addr = s.accept()
print("\n***Connection established")

buffer = b""
while len(buffer) < 4:
    packet = conn.recv(4 - len(buffer))
    buffer += packet

header = buffer
message_length = struct.unpack('!I', header)[0]

buffer = b""
while len(buffer) < message_length:
    packet = conn.recv(message_length - len(buffer))
    buffer += packet
full_data = buffer
msg = pickle.loads(full_data)

data = pandas.DataFrame.from_dict(msg).set_index('timestamp')

X = []
for row in data :
    X.append(row.values)

X = array(X, dtype ='float32')

print(X)
