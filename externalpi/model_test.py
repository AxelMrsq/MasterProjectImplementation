from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input

model = Sequential() 
model.add(Input(shape = (24, 5))) 
model.add(LSTM(32, return_sequences=True)) 
model.add(LSTM(16))
model.add(Dense(1)) 
model.save("local_model.keras")

