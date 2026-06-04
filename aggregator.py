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

import os

import pandas



# Class representing aggregator on virtual private server 
class Aggregator :


    # Method for initialisation
    def __init__(self):
        print("Execuing method '__init__'...")
        
        # Checking if there is already a global model save
        if not("global_model.keras" in os.listdir(os.getcwd())) :
            # Initialising global model 
            print("\nCreating global model *via function*")
            self.global_model_path = createModel("global_model.keras")
        
        # Reading from nodes.csv nodes informations
        print("\nLoading nodes informations")
        self.nodes = pandas.read_csv("nodes.csv")
    

    # Method for running the aggregator 
    def startServer(self):
        print("Execuing method 'startServer'...")

        # Catching error loop to avoid freeze
        try:
            print("\nTrying...")

            # Creating internet connection
            print("\nCreating socket")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

            # Setting parameters of the server connection
            print("Parametring socket")
            s.bind(('0.0.0.0', 65432))

            # Listening for connection
            print("Listening on {'0.0.0.0'}:{65432}")
            s.listen()
            
            # Getting information about the connection
            print("Waiting for connection")
            conn, addr = s.accept()
            print("Connection detected...")
            print(f"\nConnected by {addr}")

            # # Waiting for message
            # print("\nWaiting for message")
            # data = conn.recv(4096)
            
            # # Decode the message in Byte
            # print("Decoding message")
            # msg = data.decode('utf-8')
            # print(f"Received : {msg}")

            data = b""
            while True:
                packet = s.recv(30410)
                if not packet: break
                data += packet

                
            # Dersializing the answer (global parameters)
            print("Local : Deserializing the answer")
            msg = pickle.loads(data)
            
            # Catching error loop to avoid freeze
            try:
                print("\nTrying...")
                
                # Check the msg format
                print("Checking message format")
                token, command, value = msg.split(':')

                # Setting msg valid
                print("Validating the message")
                msg_valid = True

            # Catching error
            except ValueError:
                print("Except...")

                # Sending error message back
                print("\nSending error message : String does not match the 'TOKEN:COMMAND:VALUE' format")
                conn.sendall(b"String does not match the 'TOKEN:COMMAND:VALUE' format")
                
                # Setting msg unvalid
                print("Setting message unvalid")
                msg_valid = False
            
            # If msg is valid
            if msg_valid == True :
                print("Reading the message")
                 
                #  If token exist 
                if int(token) in self.nodes["id"] :
                    print(f"Token identified as {int(token)}")

                    # Ping pong command management
                    if command == "ping":
                        print("Managing 'ping' command...")

                        # Answer back "Pong"
                        print("\nSending back 'Pong'")
                        conn.sendall(b"Pong")

                    # send global parameters command management
                    elif command == "sendglobalparameters" :
                        print("Managing sendglobalparameters command...")
                        
                        # Getting serialized global parameters
                        print("Local : Getting serialized global parameters *via function*")
                        serialized_global_parameters = self.getSerializedGlobalParameters()
                        
                        # Sending serialized global parameters
                        print("Socket : Sending serialized global parameters")
                        conn.sendall(serialized_global_parameters)
                    
                    # get local parameters command management
                    elif command == "getlocalparameters" :
                        print("Managing getlocalparameters command...")
                        
                        # Saving local parameters
                        print(f"\nSaving local parameters from {int(token)}")
                        # self.getLocalParameters(value, token)

            # if msg not valid
            else :
                print("Ending the communication")

                # Closing the connection
                print("\nClosing the connection")
                conn.close()

        # Catching keyboard interruption
        except KeyboardInterrupt:
            print("Except...")
            print("\nDeconnected")

        finally :
            print("Shutting down server")

            # Closing the socket
            print("\nClosing the socket")
            s.close()


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
    def aggregate(self, local_parameters_1 , local_parameters_2):
        print("Execuing method 'getLocalParameters'...")

        # create an empty parameters array
        print("Local : Creating an empty parameters array")
        aggregated_parameters = []

        # Formating with the correct size the empty parameters array
        print("Local : Formating the aggregated parameters array")
        for parameters_layer in local_parameters_1 :

            # Adding each layers initialized at 0
            print("\nLocal : Modifying size (for loop)")
            aggregated_parameters.append(numpy.zeros_like(parameters_layer))

        # Summing layers
        print("Local : Summin different nodes layers")
        for i in range(len(aggregated_parameters)) :

            # Adding each layers iteratively
            print(f"\nLocal : Adding layers {i}")
            aggregated_parameters[i] = local_parameters_1[i] + local_parameters_2[i]

        # Creating final parameters array
        print("Local : Creating the final global parameters array")
        final_parameters = []

        # Averaging layers
        print("Local : Avering different nodes layers")
        n = 0
        for parameters_layer in aggregated_parameters :

            # Averaging each layers iteratively
            print(f"Local : Averging layers {n}")
            n+=1
            final_parameters.append(parameters_layer / 2)
        
        # Loading global model
        print("Local : Loading global model")
        global_model = load_model(self.global_model_path)

        # Setting parameters of the global model with the new one
        print("Local : Setting parameters into the global model")
        global_model.set_weights(final_parameters)

        # Saving the global model
        print("Local : Saving the global model")
        global_model.save(self.global_model_path)




ag = Aggregator()

ag.startServer()