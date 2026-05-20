# Package for internet communication
import socket

# Package for serialization and reverse
import pickle

# Package for managing model object 
from tensorflow.keras.models import load_model

# Self made model creation functions
from model import createModel



# Class representing edge local computer
class Node :


    # Method for initialisation 
    def __init__(self):
        print("Execuing method '__init__'...")
        
        # Initialising local model 
        print("Local : Creating local model *via function*")
        self.local_model_path = createModel("local_model.keras")


    # Method to send local paramaters to the aggregator
    def sendSerializedLocalParameters(self):
        print("Executing method 'sendSerializedLocalParameters'...")
        
        # Catching error loop to avoid freeze
        try:
            print("Trying...")

            # Creating internet connection
            print("Socket : Creating socket")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
             
            # Connect 
            print("Socket : Connecting to server {'192.168.1.34'}")
            s.connect(('192.168.1.34', 65432))
            
            # Send a message
            print("Socket : Sending command {'getlocalparameters'}")
            s.sendall(b"getlocalparameters")
            
            # Get serialized local parameters
            print("Local : Getting serialized local parameters *via function*")
            serialized_Local_parameters = self.getSerializedLocalParameters()
            
            # Waiting for answer
            print("Socket : Waiting for answer")
            data = s.recv(30410)
            
            # Send serialized local parameters
            print("Socket : Sending serialized local parameters")
            s.sendall(serialized_Local_parameters)
            
            # Closing the internet connection
            print("Socket : Closing")
            s.close()

        # End script manually 
        except KeyboardInterrupt:
            print("Except...")
            print("\nSocket : Deconnected")

        # Catching server error
        except ConnectionRefusedError:
            print("Except...")
            print("Socket : Connection refused")


    # Method to get local serialized parameters
    def getSerializedLocalParameters(self) :
        print("Executing method 'getSerializedLocalParameters'...")

        # Loading the local model
        print("\n*Local : Loading the local model*")
        local_model = load_model(self.local_model_path)
        
        # Getting parameters from the local model
        print("*Local : Getting parameters from the local model*")
        local_parameters = local_model.get_weights()
        
        # Serializing local parameters and returning local parameters
        print("*Local : Returning serialized local parameters*")
        return pickle.dumps(local_parameters)
    
    
    # Method to get global parameters from the aggregator
    def getGlobalParameters(self) :
        print("Executing method 'getGlobalParameters'...")

         # Catching error loop to avoid freeze
        try:
            
            # Creating internet connection
            print("\nSockey : Creating socket")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

            # Connect
            print("Socket : Connecting to server {'192.168.1.34'}")
            s.connect(('192.168.1.34', 65432))
            
            # Send a message
            print("Socket : Sending command {'sendglobalparameters'}")
            s.sendall(b"sendglobalparameters")
            
            # Waiting for answer (global parameters)
            print("Socket : Waiting for answer")
            data = s.recv(30410)

            # Dersializing the answer (global parameters)
            print("Local : Deserializing the answer")
            global_parameters = pickle.loads(data)
            
            # Loading local model
            print("Local : Loading the local model")
            local_model = load_model(self.local_model_path)
            
            # Changing local model parameters with global parameters
            print("Local : Setting global parameters to the local model")
            local_model.set_weights(global_parameters)

            # Saving changed local model 
            print('Local : Saving new local model')
            local_model.save(self.local_model_path)
            
            # Closing internet connection
            print("Socket : Closing")
            s.close()
        
        # End script manually 
        except KeyboardInterrupt:
            print("\nDeconnected...")
        
        # Catching server error
        except ConnectionRefusedError:
            print("Error : Connection refused")


n = Node()

# n.sendSerializedLocalParameters()

n.getGlobalParameters()