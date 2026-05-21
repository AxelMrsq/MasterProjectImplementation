# Package for internet communication
import socket

# Package for serialization and reverse
import pickle

# Package for managing model object 
from tensorflow.keras.models import load_model

# Package to manage array
import numpy

# Self made model creation functions
from model import createModel



# Class representing aggregator on virtual private server 
class Aggregator :


    # Method for initialisation
    def __init__(self):
        print("Execuing method '__init__'...")
        
        # Initialising local model 
        print("\nLocal : Creating global model *via function*")
        self.global_model_path = createModel("global_model.keras")
        
    
    # Method for running the aggregator 
    def startServer(self):
        print("Execuing method 'startServer'...")

        # Catching error loop to avoid freeze
        try:
            print("\nTrying...")

            # Creating internet connection
            print("\nSocket : Creating socket")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

            # Setting parameters of the server connection
            print("Socket : Parametring socket")
            s.bind(('0.0.0.0', 65432))

            # Listening for connection
            print("Socket : Listening on {'0.0.0.0'}:{65432}")
            s.listen()
            
            # Getting information about the connection
            print("Socket : Waiting for connection")
            conn, addr = s.accept()
            print("Connection detected...")
            print(f"\nSocket : Connected by {addr}")

            # Waiting for message
            print("\nSocket : Waiting for message")
            data = conn.recv(30410)
            
            # Decode the message in Byte
            print("Local : Decoding message")
            msg = data.decode('utf-8')
            print(f"Socket : Received : {msg}")
            
            # Ping pong command management
            if msg == "ping":
                print("Managing ping command...")
                conn.sendall(b"Pong")

            # send global parameters command management
            elif msg == "sendglobalparameters" :
                print("Managing sendglobalparameters command...")
                
                # Getting serialized global parameters
                print("Local : Getting serialized global parameters *via function*")
                serialized_global_parameters = self.getSerializedGlobalParameters()
                
                # Sending serialized global parameters
                print("Socket : Sending serialized global parameters")
                conn.sendall(serialized_global_parameters)
            
            # get local parameters command management
            elif msg == "getlocalparameters" :
                print("Managing getlocalparameters command...")

                # Confirm the reception of the command to received local parameters
                print("Socket : Confirming reception of the command")
                conn.sendall(b"Pong")
                
                # Waiting for message
                print("Socket : Waiting for message")
                data = conn.recv(30410)

                # Deserializing message
                print("Local : Deserializing message")
                message = pickle.loads(data)
                
                # Saving local model save 
                print("Local : saving local model save *via function*")
                self.getLocalParameters(message, addr)

        # Catching error loop to avoid freeze
        except KeyboardInterrupt:
            print("Except...")
            print("\nSocket : Deconnected")


    # Method for getting serialized global parameters
    def getSerializedGlobalParameters(self) :
        print("Execuing method 'getSerializedGlobalParameters'...")

        # Loading global model
        print("Local : Loading global model")
        global_model = load_model(self.global_model_path)

        # Getting global parameters
        print("Local : Getting global parameters")
        global_parameters = global_model.get_weights()

        # Returning serialized global parameters
        print("Local : Returning serialized global parameters")
        return pickle.dumps(global_parameters)
    
    
    # Method for saving local model save
    def getLocalParameters(self, local_parameters, node) :
        print("Execuing method 'getLocalParameters'...")

        # Create a duplicata of the local model
        print("Local : creating a duplicata of the local model")
        local_model_path = createModel(f"local_model_{node}.keras")

        # Load the local model
        print("Local : Loading the duplicata of the local model")
        local_model = load_model(local_model_path)

        # Setting weights of the local model
        print("Local : Setting received local parameters into the local model duplicata ")
        local_model.set_weights(local_parameters)

        # Saving local model duplicata
        print("Local : Saving local model duplicata")
        local_model.save(local_model_path)


    # Method to do the aggregation (mean of layers)
    def aggregate(self, local_parameters_list):
        print("Execuing method 'getLocalParameters'...")

        # create an empty parameters array
        print("Local : Creating an empty parameters array")
        aggregated_parameters = []

        # Formating with the correct size the empty parameters array
        print("Local : Formating the aggregated parameters array")
        for parameters_layer in local_parameters_list[0] :

            # Adding each layers initialized at 0
            print("\nLocal : Modifying size (for loop)")
            aggregated_parameters.append(numpy.zeros_like(parameters_layer))

        # Summing layers
        print("Local : Summin different nodes layers")
        for i in range(len(aggregated_parameters)) :

            # Adding each layers iteratively
            print(f"\nLocal : Adding layers {i}")
            aggregated_parameters[i] = local_parameters_list[0] + local_parameters_list[1]

        # Creating final parameters array
        print("Local : Creating the final global parameters array")
        final_parameters = []

        # Averaging layers
        print("Local : Avering different nodes layers")
        for parameters_layer in aggregated_parameters :

            # Averaging each layers iteratively
            print(f"Local : Averging layers {i}")
            final_parameters.append(parameters_layer / 2)
        
        # Loading global model
        print("Local : Loading global model")
        global_model = load_model(self.global_model_path)
        global_model.set_weights(final_parameters)
        global_model.save(self.global_model_path)




ag = Aggregator()
ag.startServer()