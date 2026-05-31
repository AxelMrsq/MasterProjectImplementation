# Package for internet communication
import socket

# Package for serialization and reverse
import pickle

# Package for managing model object 
from tensorflow.keras.models import load_model

# Self made model creation functions
from model import createModel

# Manage json files
# https://www.w3schools.com/python/python_json.asp
import json

# Manage pandas dataframe/csv
import pandas

# Manage numpy array
import numpy 

# Class representing edge local computer
class Node :


    # Method for initialisation 
    def __init__(self):
        print("Execuing method '__init__'...")
        
        # # Initialising local model 
        # print("Local : Creating local model *via function*")
        # self.local_model_path = createModel("local_model.keras")
        
        # # Openning the json secret file
        # print("Local : Reading json file")
        # jsonFile = open('vps.json', 'r', encoding='utf-8')

        # # Setting up the aggregator ip
        # print("Local : Getting the aggregator ip")
        # self.ag_ip = json.load(jsonFile)["ip"]


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
            print(f"Socket : Connecting to server {self.ag_ip}")
            s.connect((self.ag_ip, 65432))
            
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
            print(f"Socket : Connecting to server {self.ag_ip}")
            s.connect((self.ag_ip, 65432))
            
            # Send a message
            print("Socket : Sending command {'sendglobalparameters'}")
            s.sendall(b"sendglobalparameters")
            
            # Waiting for answer (global parameters)
            # print("Socket : Waiting for answer")
            # data = s.recv(30410)
            

            # https://stackoverflow.com/questions/44637809/python-3-6-socket-pickle-data-was-truncated
            data = b""
            while True:
                packet = s.recv(4096)
                if not packet: break
                data += packet

                

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


    # def trainLocalModel(self) :
        # print("Executing method 'trainLocalModel'...")

        # load data for training
        # print("Local : Loading data *via function* ")
        # X_train, y_train, X_val, y_val, X_test, y_test = loadData("proto_data.csv")

        # Load local model
        # print("Local : Loading local model")
        # local_model = load_model(self.local_model_path)

        # Fitting local model
        # print("Local : Fitting local model")
        # local_model.fit()

        # Saving local model
        # print("Local : Saving local model")
        # local_model.save(self.local_model_path)


    # def inferWithLocalModel(self) :
        # print("Executing method 'inferWithLocalModel'...")

        # Loading local model
        # print("Local : Loading local model")
        # local_model = load_model(self.local_model_path)

        # Predict new data with local model
        # print("Local : Predicting new data")
        # new_data = local_model.predict()

    def loadData(self, path) :
        print("Executing method 'loadData'...")

        data = pandas.read_csv(path, sep=";")

        features_col = ["Consumption", "Weekday", "Hour", "AVG4D (kWh)", "TempCluster"]
        target_col = "Consumption"

        samples = []
        
        # https://www.youtube.com/watch?v=yF6Jrzz7E5s
        for i in range(0,len(data)-1) :
            
            features = data.loc[i-23:i][features_col]
            target = data.loc[i+1][target_col]
            

            sample = {"features" : features, "target": target}
            
            samples.append(sample)
        
        # print(samples[2]["features"])
        # print(samples[1]["target"])
        
        # https://www.tensorflow.org/api_docs/python/tf/keras/utils/pad_sequences
        from tensorflow.keras.preprocessing.sequence import pad_sequences

        features_list = [sample["features"] for sample in samples]

        X_train = pad_sequences(features_list[:int(len(samples)*0.85)], padding='pre', dtype='float32')
        X_val= pad_sequences(features_list[int(len(samples)*0.80):int(len(samples)*0.90)], padding='pre', dtype='float32')
        X_test = pad_sequences(features_list[int(len(samples)*0.90):], padding='pre', dtype='float32')

        targets_list = [sample["target"] for sample in samples]

        y_train = numpy.array(targets_list[:int(len(samples)*0.85)], dtype='float32')
        y_val = numpy.array(targets_list[int(len(samples)*0.80):int(len(samples)*0.90)], dtype='float32')
        y_test = numpy.array(targets_list[int(len(samples)*0.90):], dtype='float32')

        # print(X_train_padded.shape)
        # print(y_train.shape)

        # print(X_val_padded.shape)
        # print(y_val.shape)

        # print(X_test_padded.shape)
        # print(y_test.shape)       

        # return X_train, y_train, X_val, y_val, X_test, y_test tensorflow sets
        print("Local : Returning X_train, y_train, X_val, y_val, X_test, y_test tensorflow sets")
        return X_train, y_train, X_val, y_val, X_test, y_test


n = Node()

n.loadData("proto_data.csv")