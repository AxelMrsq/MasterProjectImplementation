from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Input, Dense
from tensorflow.keras.optimizers import SGD
from tensorflow.keras import backend 
from pickle import loads, dumps
from pandas import read_csv
from numpy import array
import socket



def initiateGlobalModel():
    model = Sequential()
    model.add(Input(shape = (24, 5)))  
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1)) 
    model.save("global_model.keras") 

def start():
    initiateGlobalModel()
    global_model = load_model("global_model.keras")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind(('0.0.0.0', 65432))
    s.listen()


    conn, addr = s.accept()

    msg = loads(conn.recv(4096))

    for i in range(5) :

        conn.sendall(dumps(global_model.get_weights()))

        msg = loads(conn.recv(4096))

        id = msg["id"]

        key = msg["cmd"]

        parameters = msg["parameters"]

        key = msg["key"]



    