import socket

class Aggregator :
    def __init__(self):
        pass

    
    def start_server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.bind(('0.0.0.0', 65432))
            s.listen()
            print(f"Server listening on {'0.0.0.0'}:{65432}...")
            
            # This line makes the program "pause" and wait. It sits there until someone tries to connect
            conn, addr = s.accept()

            # Python will automatically close the connection for you once the code inside that block finishes, even if the program crashes
            with conn:

                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    print(f"Received : {message}")
                    
                    if message.lower() == "ping":
                        conn.sendall(b"Pong")
                    else:
                        conn.sendall(b"Message received")
        except KeyboardInterrupt:
            print("\nStopping...")

ag = Aggregator()

ag.start_server()