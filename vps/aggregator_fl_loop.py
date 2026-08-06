from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Input, Dense
from pickle import loads, dumps
import socket
from numpy import zeros_like
import threading
import struct

round_barrier = threading.Barrier(2)

def initiateGlobalModel():
    model = Sequential()
    model.add(Input(shape = (24, 5)))  
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1)) 
    model.save("global_model.keras") 


def handleClient(port):
    print("\nThread : Creating Socket")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind(('0.0.0.0', port))
    print("Thread : Check")

    print("\nThread : Opening Socket")
    s.listen()
    print("Thread : Check")
    
    print("\nThread : Accepting Socket")
    conn, addr = s.accept()
    print("Thread : Check")
    
    print("\nThread : Receiving GET cmd")
    buffer = b""
    while len(buffer) < 4:
        packet = conn.recv(4 - len(buffer))
        buffer += packet
    
    header = buffer
    message_length = struct.unpack('!I', header)[0]

    print(f"message rcv length : {message_length}")

    buffer = b""
    while len(buffer) < message_length:
        packet = conn.recv(message_length - len(buffer))
        buffer += packet
    full_data = buffer
    msg = loads(full_data)

    client_id = msg["id"]
    print("Thread : Check")
    
    key = msg["key"] 
    r = 0 
    
    
    while key == True :
        print(f"r = {r}")
        r+=1
        print(f"\nThread client id {client_id} : key={key}")

        print(f"\nThread client id {client_id} : Sending POST cmd")

        global_model = model_dict[client_id]
    
        
        message = dumps({"id":client_id,"cmd": "POST","key":key, "value":global_model.get_weights()})
        header = struct.pack('!I', len(message))

        print(f" client id {client_id} message sent length : {len(message)}")
        conn.sendall(header + message)

        
        print(f"Thread client id {client_id} : Check")
        
        print(f"\nThread client id {client_id} : Receiving POST cmd")

        buffer = b""
        while len(buffer) < 4:
            packet = conn.recv(4 - len(buffer))
            buffer += packet
        
        header = buffer
        message_length = struct.unpack('!I', header)[0]
        print(f" client id {client_id} message rcv length : {message_length}")
        

        buffer = b""
        while len(buffer) < message_length:
            packet = conn.recv(message_length - len(buffer))
            buffer += packet
        full_data = buffer


       

        local_parameters = loads(full_data)["value"]
        key = loads(full_data)["key"]


        global_model.set_weights(local_parameters)

        model_dict[client_id] = global_model
        print(f" client id {client_id} Thread : Check")
        
        print(f"\n client id {client_id} Thread : Waiting for other client")
        barrier_idx = round_barrier.wait()
        print(f" client id {client_id}Thread : Check")
        
        
        if barrier_idx == 0:
            print(f"\n client id {client_id} Thread : Aggregate")
            aggregated_parameters = []

            parameters_1 = model_dict[0].get_weights()
            parameters_2 = model_dict[1].get_weights()

            for parameters_layer in parameters_1 :
                aggregated_parameters.append(zeros_like(parameters_layer))

            for i in range(len(aggregated_parameters)) :
                aggregated_parameters[i] = parameters_1[i] + parameters_2[i]

            final_parameters = []

            n = 0
            for parameters_layer in aggregated_parameters :
                n+=1
                final_parameters.append(parameters_layer / 2)

            model_dict[0].set_weights(final_parameters)
            model_dict[1].set_weights(final_parameters)
                


        round_barrier.wait()
        print(f" client id {client_id} Thread : Check")

    print(f"\n client id {client_id} Thread : Sending POST cmd")
    global_model = model_dict[client_id]

    header = struct.pack('!I', len(message))

    print(f" client id {client_id} message sent length : {len(message)}")
        
    message = dumps({"id":client_id,"cmd": "POST","key":key, "value":global_model.get_weights()})
    conn.sendall(header + message)

    print(f" client id {client_id} Thread : Check")

    

def start():

    conn_nb = 0
    threads = []
    
    print("Initiating global model...")
    initiateGlobalModel()
    global_model = load_model("global_model.keras")
    print("Check")

    global model_dict

    model_dict = {0: global_model, 1: global_model}



    client_1 = threading.Thread(target=handleClient, args=(65433,))
    client_2 = threading.Thread(target=handleClient, args=(65432,))

    
    client_1.start()

     
    client_2.start()

    client_1.join()
    client_2.join()
start()