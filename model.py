from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.models import Sequential


def getmodel() :
    model = Sequential()
    model.add(Input(shape = (24, 5)))
    model.add(LSTM(32, return_sequences=True))
    model.add(LSTM(16))
    model.add(Dense(1))
    return model


def createModel(path) :
    model = getmodel()
    model.save(path)
    return path