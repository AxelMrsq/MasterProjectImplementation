# Package for managing tensorflow model layers objects
from tensorflow.keras.layers import LSTM, Dense, Input # Class of LSTM, Dense and input layers

# Package for managing tensorflow model objects
from tensorflow.keras.models import Sequential # Class of model initializer

def createModel(path) :
    model = Sequential()
    model.add(Input(shape = (24, 5)))
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1))
    model.save(path)
    return path

def checkIf