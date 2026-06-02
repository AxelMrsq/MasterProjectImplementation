import socket


def startClient():
    try:
        print("Trying...")

        # Creating internet connection
        print("Socket : Creating socket")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            
        # Connect 
        print("Socket : Connecting to server 192.168.1.55")
        s.connect(("192.168.1.55", 65432))
        
        # Send a message
        print("Socket : Sending command {'getlocalparameters'}")
        s.sendall(b"getlocalparameters")
    
    # End script manually 
    except KeyboardInterrupt:
        print("Except...")
        print("\nSocket : Deconnected")

    # Catching server error
    except ConnectionRefusedError:
        print("Except...")
        print("Socket : Connection refused")

startClient()