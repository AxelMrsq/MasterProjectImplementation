import socket

class Node :
    def __init__(self):
        pass

    def start_client(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect(('192.168.1.34', 65432))
            print(f"Connecté au serveur {'192.168.1.34'}")
                
           
            print("Envoi : Ping")
            s.sendall(b"Ping")
            
            data = s.recv(1024)
            print(f"Reçu du serveur : {data.decode('utf-8')}")
                
                
        except KeyboardInterrupt:
            print("\nDéconnexion...")
        except ConnectionRefusedError:
            print("Error : Connection refused")

n = Node()
n.start_client()