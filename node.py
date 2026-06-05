import socket # Package for managing internet communication
import pickle # Package for managing serialiszation of message
import json # Package for managing json files
import pandas # Package for managing csv files
import numpy # Package for managing numpy array

import os
# 1. Suppress TensorFlow's internal logging
# '0' = all logs shown (default)
# '1' = filter out INFO logs
# '2' = filter out INFO and WARNING logs
# '3' = filter out INFO, WARNING, and ERROR logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"

# Package for managing tensorflow model objects
from tensorflow.keras.models import load_model # Function to load model from .keras files

# Package for managing tensorflow model optimizers for training
from tensorflow.keras.optimizers import SGD # Class for stochastic gradient descent objects

# Package for managing timeseries data sequence
from tensorflow.keras.preprocessing.sequence import pad_sequences # Package for managing data sample of different size

# Package for managing tensorflow model layers objects
from tensorflow.keras.layers import LSTM, Dense, Input # Class of LSTM, Dense and input layers

# Package for managing tensorflow model objects
from tensorflow.keras.models import Sequential # Class of model initializer


# Class representing the edge node from the federated learning architecture 
class Node :

    
    # Node objects initialising method (No input, No return)
    def __init__(self):
        print("Method '__init__' : Initialising a node object")
        
        print("Method '__init__' : Checking if 'local_model.keras' file exists in the current directory")

        # Function for getting current directory path
        current_directory = os.getcwd() # https://docs.python.org/3/library/os.html#os.getcwd
        
        # Function for getting the list of files in the given directory (Here : current directory)
        current_directory_files = os.listdir(current_directory) # https://docs.python.org/3/library/os.html#os.listdir

        if not("local_model.keras" in current_directory_files) :
            print("Method '__init__' : No local model save detected => Creating a local model following the architecture from https://ieeexplore.ieee.org/abstract/document/9469923")
            
            # Initialize a model object 
            model = Sequential() # https://www.tensorflow.org/api_docs/python/tf/keras/Sequential
            # Adding an input layer for 24 times steps and 5 features
            model.add(Input(shape = (24, 5)))  # https://www.tensorflow.org/api_docs/python/tf/keras/Input
            # Adding an LSTM layer with 32 cells
            model.add(LSTM(32, return_sequences=True)) # https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
            # Adding an LSTM layer with 16 cells
            model.add(LSTM(16))
            # Adding a Dense layer with 1 neurone as output
            model.add(Dense(1)) # https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense

            # Saving the model object as a keras file in current directory as "local_model.keras"
            model.save("local_model.keras") # https://www.tensorflow.org/api_docs/python/tf/keras/Model#save
            
            # Setting the local_model_path attribute as "local_model.keras"
            self.local_model_path = "local_model.keras"

            print(f"Method '__init__' : Local model saved in current directory as {self.local_model_path}")

        else : 
            print("Method '__init__' : Local model save detected")

            # Setting the local_model_path attribute as "local_model.keras"
            self.local_model_path = "local_model.keras"
        

        
        jsonFile = open('vps.json', 'r', encoding='utf-8')
        data = json.load(jsonFile)
        jsonFile.close()

        self.ag_ip = data["ip"]
        
        self.token = int(data["token"])


    def sendSerializedLocalParameters(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((self.ag_ip, 65432))
            
            local_model = load_model(self.local_model_path)
    
            local_parameters = local_model.get_weights()
            
            message = {"token":self.token,"command":"getLocalParameters","value":local_parameters}
            s.sendall(pickle.dumps(message))
            
        except KeyboardInterrupt:
            s.close()

        except ConnectionRefusedError:
            s.close()

        finally:
            s.close()
    

    def getGlobalParameters(self) :
        try:
            print("\n***Starting socket")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((self.ag_ip, 65432))
    
            print("\n***Connected")

            message = {"token":self.token,"command":"sendGlobalParameters","value":None}
            s.sendall(pickle.dumps(message))

            print("\n***Message sent")
            
            # https://stackoverflow.com/questions/44637809/python-3-6-socket-pickle-data-was-truncated
            encoded_data = b""
            while True:
                packet = s.recv(4096)
                if not packet: break
                encoded_data += packet
            
            global_parameters =  pickle.loads(encoded_data)

            local_model = load_model(self.local_model_path)
            local_model.set_weights(global_parameters)
            local_model.save(self.local_model_path)    
        
        except KeyboardInterrupt:
            s.close()
        
        except ConnectionRefusedError:
            s.close()
        
        finally:
            s.close()


    def trainLocalModel(self) :
        X_train, y_train, X_val, y_val, X_test, y_test = self.loadData("proto_data.csv")

        local_model = load_model(self.local_model_path)
        local_model.compile(optimizer=SGD(learning_rate=0.0001) , loss='mse')
        local_model.fit(x=X_train, y=y_train, validation_data=(X_val, y_val), epochs=5, batch_size = 100) # https://www.tensorflow.org/api_docs/python/tf/keras/Model#fit
        local_model.save(self.local_model_path)


    def inferWithLocalModel(self, input_data) :
        local_model = load_model(self.local_model_path)
        return local_model.predict(input_data)

    def loadData(self, path) :
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
        

        features_list = [sample["features"] for sample in samples]
        
        # https://www.tensorflow.org/api_docs/python/tf/keras/utils/pad_sequences
        X_train = pad_sequences(features_list[:int(len(samples)*0.85)], padding='pre', dtype='float32')
        X_val= pad_sequences(features_list[int(len(samples)*0.80):int(len(samples)*0.90)], padding='pre', dtype='float32')
        X_test = pad_sequences(features_list[int(len(samples)*0.90):], padding='pre', dtype='float32')

        targets_list = [sample["target"] for sample in samples]

        y_train = numpy.array(targets_list[:int(len(samples)*0.85)], dtype='float32')
        y_val = numpy.array(targets_list[int(len(samples)*0.80):int(len(samples)*0.90)], dtype='float32')
        y_test = numpy.array(targets_list[int(len(samples)*0.90):], dtype='float32')

        return X_train, y_train, X_val, y_val, X_test, y_test


