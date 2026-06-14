from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Input, Dense
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import backend 
from pickle import loads, dumps
from pandas import read_csv
from numpy import array
import socket


def initiateLocalModel():
    model = Sequential()
    model.add(Input(shape = (24, 5)))  
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1)) 
    model.save("local_model.keras") 

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


def start():
    initiateLocalModel()

    X_train, X_val, X_test, y_train, y_val, y_test = loadData()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect(("83.228.240.76", 65432))

    s.sendall(dumps({"id":1,"cmd":"GET"}))

    local_model = load_model("local_model.keras")
    
    for i in range(5) :


        local_model.set_weights(loads(s.rscv(40000))["value"])

        local_model.evaluate(X_val, y_val)

        local_model.compile(optimizer=SGD(learning_rate=0.0001) , loss='mse')

        local_model.fit(x=X_train, y=y_train, epochs=5, batch_size = 100) 

        local_model.evaluate(X_val, y_val)

        s.sendall(dumps({"id":1,"cmd":"GET"}))


    local_model.set_weights(loads(s.rscv(40000))["value"])

    s.close()

    local_model.evaluate(X_val, y_val)

    local_model.compile(optimizer=SGD(learning_rate=0.0001) , loss='mse')

    local_model.fit(x=X_train, y=y_train, epochs=5, batch_size = 100) 

    local_model.evaluate(X_val, y_val)

    local_model.save("local_model.keras")
    
    backend.clear_session()






