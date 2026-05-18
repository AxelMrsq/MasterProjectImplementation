import tensorflow
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.models import Sequential

def model() :
    model = Sequential()
    model.add(Input(shape = (24, 1)))
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1))
    return model

def createModel() :
    global_model = model()
    path =  "global_model.keras"
    global_model.save(path)
    return path