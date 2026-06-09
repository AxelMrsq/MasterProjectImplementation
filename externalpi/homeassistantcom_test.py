import socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 65400))
s.listen()

conn, addr = s.accept()
           
encoded_data = conn.recv(4096)

print(encoded_data.decode("utf-8"))

conn.sendall(b"salut")