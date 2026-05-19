import socket
from model import createModel
import tensorflow
from tensorflow.keras.models import load_model
import pickle

class Aggregator :
    def __init__(self):
        self.global_model_path = createModel("global_model.keras")
        
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
                    data = conn.recv(30410)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    print(f"Received : {message}")

                    msg = message.lower()
                    
                    if msg == "ping":
                        conn.sendall(b"Pong")


                    elif msg == "sendglobalparameters" :
                        serialized_global_parameters = self.getSerializedGlobalParameters()
                        conn.sendall(serialized_global_parameters)


                    elif msg == "aggregate" :
                        self.aggregate()

                    elif msg == "getlocalparameters" :
                        conn.sendall(b"Pong")
                    
                        data = conn.recv(30410)
                        message = pickle.loads(data)
                        print(f"Received : {message}") 


                        self.getLocalParameters(message, addr)


                    else:
                        conn.sendall(b"Message received")

        except KeyboardInterrupt:
            print("\nStopping...")

    def getSerializedGlobalParameters(self) :
        global_model = load_model(self.global_model_path)
        global_parameters = global_model.get_weights()
        return pickle.dumps(global_parameters)


    def aggregate(self) :
        pass

    def getLocalParameters(self, local_parameters, node) :
        local_model_path = createModel(f"local_model_{node}.keras")
        local_model = load_model(local_model_path)
        local_model.set_weights(local_parameters)
        

ag = Aggregator()

# ag.getSerializedGlobalParameters()

ag.start_server()