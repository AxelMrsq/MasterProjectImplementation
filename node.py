import socket
import pickle
import json
import pandas
import numpy 
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.preprocessing.sequence import pad_sequences # https://www.tensorflow.org/api_docs/python/tf/keras/utils/pad_sequences
from model import createModel


class Node :


    def __init__(self):
        if not("local_model.keras" in os.listdir(os.getcwd())) :
            self.local_model_path = createModel("local_model.keras")

        else : 
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
            
            message = {"token":self.token,"command":"sendLocalParameters","value":local_parameters}
            s.sendall(pickle.dumps(message))
            
        except KeyboardInterrupt:
            s.close()

        except ConnectionRefusedError:
            s.close()

        finally:
            s.close()
    

    def getGlobalParameters(self) :
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.connect((self.ag_ip, 65432))
            
            message = {"token":self.token,"command":"getGlobalParameters","value":None}
            s.sendall(pickle.dumps(message))
            
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

        X_train = pad_sequences(features_list[:int(len(samples)*0.85)], padding='pre', dtype='float32')
        X_val= pad_sequences(features_list[int(len(samples)*0.80):int(len(samples)*0.90)], padding='pre', dtype='float32')
        X_test = pad_sequences(features_list[int(len(samples)*0.90):], padding='pre', dtype='float32')

        targets_list = [sample["target"] for sample in samples]

        y_train = numpy.array(targets_list[:int(len(samples)*0.85)], dtype='float32')
        y_val = numpy.array(targets_list[int(len(samples)*0.80):int(len(samples)*0.90)], dtype='float32')
        y_test = numpy.array(targets_list[int(len(samples)*0.90):], dtype='float32')

        return X_train, y_train, X_val, y_val, X_test, y_test


n = Node()
n.getGlobalParameters()