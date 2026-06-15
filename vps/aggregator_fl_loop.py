from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Input, Dense
from pickle import loads, dumps
import socket
from numpy import zeros_like
import threading

round_barrier = threading.Barrier(2)

def initiateGlobalModel():
    model = Sequential()
    model.add(Input(shape = (24, 5)))  
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1)) 
    model.save("global_model.keras") 


def handleClient(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind(('0.0.0.0', port))
    s.listen()

    conn, addr = s.accept()
    
    msg = loads(conn.recv(4096))

    client_id = msg["id"]
    
    key = msg["key"] 
    
    while key == True :

        global_model = model_dict[client_id]

        conn.sendall(dumps({"cmd": "POST", "value":global_model.get_weights()}))

        msg = loads(conn.recv(40000))

        local_parameters = msg["value"]
        key = msg["key"]


        global_model.set_weights(local_parameters)

        model_dict[client_id] = global_model

        barrier_idx = round_barrier.wait()

        if barrier_idx == 0:
            aggregated_parameters = []

            parameters_1 = model_dict[1].get_weights()
            parameters_2 = model_dict[2].get_weights()

            for parameters_layer in parameters_1 :
                aggregated_parameters.append(zeros_like(parameters_layer))

            for i in range(len(aggregated_parameters)) :
                aggregated_parameters[i] = parameters_1[i] + parameters_2[i]

            final_parameters = []

            n = 0
            for parameters_layer in aggregated_parameters :
                n+=1
                final_parameters.append(parameters_layer / 2)

            model_dict[1] = final_parameters
            model_dict[2] = final_parameters
                

        
        round_barrier.wait()

    

def start():

    conn_nb = 0
    threads = []

    initiateGlobalModel()
    global_model = load_model("global_model.keras")

    global model_dict

    model_dict = {1: global_model, 2: global_model}



    client_1 = threading.Thread(target=handleClient, args=(65433))
    client_2 = threading.Thread(target=handleClient, args=(65432))

    
    client_1.start()

     
    client_2.start()
    


    