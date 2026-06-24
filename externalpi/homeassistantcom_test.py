
import socket
import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 65432))
s.listen()

print("\n***Socket started, waiting for connection")
conn, addr = s.accept()
print("\n***Connection established")

encoded_data = conn.recv(40000)

print("\n***Encoded data received")

message = pickle.loads(encoded_data)
print(message)