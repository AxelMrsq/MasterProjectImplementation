import socket


def handleClient(conn, addr) :
    try:
        # Waiting for initial command message
        print(f"Socket : Waiting for message from {addr}")
        data = conn.recv(4096)
        if not data:
            return
        # Decode the message
        incoming_str = data.decode('utf-8')
        try:
            if ":" in incoming_str:
                token_part, msg = incoming_str.split(":", 1)
                
            else:
                pass
                # Fallback if the client didn't send a token in the expected format
               
        except ValueError:
            # Fallback if the token part isn't a valid integer
            conn.sendall(b"Error: Invalid token format")


    except Exception as e:
            print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Socket : Connection closed with {addr}")
     

counter_list = []
counter = 0
def startServer():
    print("Executing method 'startServer'...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 65432))
        s.listen()
        print("Socket : Listening on 0.0.0.0:65432")

        conn, addr = s.accept()

        handleClient(conn, addr, socket)
    except KeyboardInterrupt:
            print("\nServer shutting down via KeyboardInterrupt.")
    finally:
        s.close()

startServer()