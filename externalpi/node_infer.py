import socket
import pickle
import struct
import pandas
import numpy
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

data = pandas.DataFrame.from_dict(msg)

data = data.drop('timestamp', axis=1)

# Conserver toutes les lignes à partir de l'index 1 (donc exclure la ligne 0)
data = data.iloc[1:]


data = data.astype({
    'hour': int,
    'weekday' : int,
    'consumption': int,
    'avg4d': int,
    'tempcluster': int,
    })


X = data.to_numpy()

X = numpy.expand_dims(X, axis=0)


print(X)


local_model = load_model("local_model.keras")

prediction = local_model.predict(X)

print(prediction[0])


message = pickle.dumps(prediction[0])
header = struct.pack('!I', len(message))
conn.sendall(header + message)

conn.close()