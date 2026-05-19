import socket
import pickle
from model import createModel
from tensorflow.keras.models import load_model

class Node :
    def __init__(self):
        self.local_model_path = createModel("local_model.keras")


    def start_client(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect(('192.168.1.34', 65432))
            print(f"Connecté au serveur {'192.168.1.34'}")
                
           
            print("Envoi : sendglobalparameters")
            # s.sendall(b"sendglobalparameters")

            s.sendall(b"getlocalparameters")


            serialized_Local_parameters = self.getSerializedLocalParameters()

            data = s.recv(30410)
            
            s.sendall(serialized_Local_parameters)
            
            # data = s.recv(30410)
            # print(f"Reçu du serveur : {pickle.loads(data)}")
                
                
        except KeyboardInterrupt:
            print("\nDéconnexion...")
        except ConnectionRefusedError:
            print("Error : Connection refused")

    
    def getSerializedLocalParameters(self) :
        local_model = load_model(self.local_model_path)
        local_parameters = local_model.get_weights()
        return pickle.dumps(local_parameters)
    

n = Node()
n.start_client()