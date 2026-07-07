import socket
import pickle
import struct
import pandas
from tensorflow.keras.models import load_model

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

data = data.astype({
    'hour': int,
    'weekday' : int,
    'consumption': float,
    'avg4d': float,
    'tempcluster': bool,
})


X = data.to_numpy()

print(X)

local_model = load_model("local_model.keras")

prediction = local_model.predict(X)

print(prediction)
