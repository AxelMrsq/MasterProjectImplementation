from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Input, Dense
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import backend 
from pickle import loads, dumps
import pandas
from pandas import read_csv
from numpy import array
import socket
import struct

def initiateLocalModel():
    model = Sequential()
    model.add(Input(shape = (24, 5)))  
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1)) 
    model.save("local_modelbis.keras") 

    backend.clear_session()


def loadData(path) :
    # 1. Read data
    data = read_csv(path, sep=";")

    features_col = ["Consumption", "Weekday", "Hour", "AVG4D (kWh)", "TempCluster"]
    target_col = "Consumption"

    features_list = []
    targets_list = []

    # 2. Populate lists directly (skipping the heavy dictionary structure)
    for i in range(0, len(data) - 1):
        features_list.append(data.loc[i-23:i][features_col].values) # .values extracts raw numpy array
        targets_list.append(data.loc[i+1][target_col])
    
    # 3. Calculate split indices
    total_samples = len(features_list)
    split_80 = int(total_samples * 0.80)
    split_85 = int(total_samples * 0.85)
    split_90 = int(total_samples * 0.90)

    # 4. Generate final arrays
    X_train = pad_sequences(features_list[:split_85], padding='pre', dtype='float32')
    X_val = pad_sequences(features_list[split_80:split_90], padding='pre', dtype='float32')
    X_test = pad_sequences(features_list[split_90:], padding='pre', dtype='float32')

    y_train = array(targets_list[:split_85], dtype='float32')
    y_val = array(targets_list[split_80:split_90], dtype='float32')
    y_test = array(targets_list[split_90:], dtype='float32')

    # 5. Return the clean arrays
    return X_train, X_val, X_test, y_train, y_val, y_test


def start(port):
    print("Initiating local model...")
    initiateLocalModel()
    print("Check")


    print("\nSaving local data...")
    X_train, X_val, X_test, y_train, y_val, y_test = loadData("proto_data.csv")
    print("check")
    
    print("\nCreating socket")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    print("check")

    print("\nconnecting to socket")
    s.connect(("83.228.240.76", port))
    print("check")
    
    print("\n send GET cmd")
    
    message = dumps({"id":1,"cmd":"GET", "key":True, "value":None})
    header = struct.pack('!I', len(message))

    s.sendall(header + message)
    print("check")

    local_model = load_model("local_modelbis.keras")
    
    for i in range(5) :

        print("\n receive POST cmd and  set global to local")

        buffer = b""
        while len(buffer) < 4:
            packet = s.recv(4 - len(buffer))
            buffer += packet
        
        header = buffer
        message_length = struct.unpack('!I', header)[0]

        buffer = b""
        while len(buffer) < message_length:
            packet = s.recv(message_length - len(buffer))
            buffer += packet
        full_data = buffer


        local_model.set_weights(loads(full_data)["value"])

        print("check")
        print("\n evaluate")
        local_model.compile(optimizer=SGD(learning_rate=0.0001) , loss='mse')
        local_model.evaluate(X_val, y_val)
        print("check")
        print("\n train")
        
         
        local_model.fit(x=X_train, y=y_train, epochs=5, batch_size = 100) 
        print("check")
        print("\n evaluate")
        local_model.evaluate(X_val, y_val)
        print("check")
        if i == 4 :
            print("\n send POST cmd")
            message = dumps({"id":1,"cmd":"POST", "key": False, "value":local_model.get_weights()})
            header = struct.pack('!I', len(message))

            s.sendall(header + message) 
            
            print("check")
        else :
            print("\n send POST cmd") 
            message = dumps({"id":1,"cmd":"POST", "key": True, "value":local_model.get_weights()})
            header = struct.pack('!I', len(message))

            s.sendall(header + message)
            print("check")

    print("\n set global to local")

    buffer = b""
    while len(buffer) < 4:
        packet = s.recv(4 - len(buffer))
        buffer += packet
    
    header = buffer
    message_length = struct.unpack('!I', header)[0]

    buffer = b""
    while len(buffer) < message_length:
        packet = s.recv(message_length - len(buffer))
        buffer += packet
    full_data = buffer


    local_model.set_weights(loads(full_data)["value"])

    print("check")

    s.close()
    print("\n evaluate")
    local_model.evaluate(X_val, y_val)
    print("check")
    print("\n train")

    local_model.compile(optimizer=SGD(learning_rate=0.0001) , loss='mse')

    local_model.fit(x=X_train, y=y_train, epochs=5, batch_size = 100) 
    print("check")
    print("\n evaluate")
    local_model.evaluate(X_test, y_test)
    print("check")
    
    print("\n save")
    local_model.save("local_model.keras")
    print("check")
    
    backend.clear_session()

import pickle

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 65400))
s.listen()

print("\n***Socket started, waiting for connection")
conn, addr = s.accept()
print("\n***Connection established")

buffer = b""
while len(buffer) < 4:
    packet = conn.recv(4 - len(buffer))
    buffer += packet

header = buffer
message_length = struct.unpack('!I', header)[0]

buffer = b""
while len(buffer) < message_length:
    packet = conn.recv(message_length - len(buffer))
    buffer += packet
full_data = buffer
msg = pickle.loads(full_data)

data = pandas.DataFrame.from_dict(msg).set_index('timestamp')

conn.close()
s.close()

data.to_csv("proto_data.csv")


start(65433)


