import socket
import pickle
import numpy
import os
import pandas
from tensorflow.keras.models import load_model
from model import createModel


class Aggregator :


    def __init__(self):
        if not("global_model.keras" in os.listdir(os.getcwd())) :
            self.global_model_path = createModel("global_model.keras")

        else :
            self.global_model_path = "global_model.keras"

        self.nodes = pandas.read_csv("nodes.csv")
    

    def startServer(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            s.bind(('0.0.0.0', 65432))
            s.listen()
            
            conn, addr = s.accept()

            encoded_data = b""
            while True:
                packet = conn.recv(4096)
                if not packet: 
                    break
                encoded_data += packet
            

            message = pickle.loads(encoded_data)

            try:
                token = message["token"]
                command = message["command"]
                value = message["value"]
         
                msg_valid = True

            except ValueError:

                conn.sendall(b"String does not match the '{'token':token,'command':command,'value':value}' format")
            
                msg_valid = False
            
            if msg_valid == True :
                if int(token) in self.nodes["id"].values:
                    if command == "ping":
    
                        conn.sendall(b"Pong")

                    elif command == "sendglobalparameters" :
                        
                            global_model = load_model(self.global_model_path)
                            global_parameters = global_model.get_weights()
                        
                            conn.sendall(picle.dumps(global_parameters))
                    
                    elif command == "getlocalparameters" :
                        local_model_path = createModel(f"local_model_{token}.keras")
                        local_model = load_model(local_model_path)
                        local_model.set_weights(value)
                        local_model.save(local_model_path)

                        
            else :
                conn.close()

        except KeyboardInterrupt:
            conn.close()
            s.close()

        finally :
            s.close()
    


    def aggregate(self, local_parameters_1 , local_parameters_2):
        aggregated_parameters = []

        for parameters_layer in local_parameters_1 :
            aggregated_parameters.append(numpy.zeros_like(parameters_layer))

        for i in range(len(aggregated_parameters)) :
            aggregated_parameters[i] = local_parameters_1[i] + local_parameters_2[i]

        final_parameters = []

        n = 0
        for parameters_layer in aggregated_parameters :
            n+=1
            final_parameters.append(parameters_layer / 2)
        
        global_model = load_model(self.global_model_path)
        global_model.set_weights(final_parameters)

        global_model.save(self.global_model_path)

