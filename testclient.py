import socket
import pickle


def startClient():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
        s.connect(("192.168.1.55", 65432))
        
        s.sendall(b"test")

        byte_message = b""
        while True:
            packet = s.recv(4096)
            if not packet: break
            byte_message += packet

        print(pickle.loads(byte_message))
    
    # End script manually 
    except KeyboardInterrupt:
        s.close()
        
    # Catching server error
    except ConnectionRefusedError:
        s.close
       
startClient()