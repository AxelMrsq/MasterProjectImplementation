from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.optimizers import SGD 
from pandas import read_csv
from numpy import array


# model = Sequential() 
# model.add(Input(shape = (24, 5))) 
# model.add(LSTM(32, return_sequences=True)) 
# model.add(LSTM(16))
# model.add(Dense(1)) 
# model.save("local_model.keras")

# model = load_model("local_model.keras")


def loadData(path) :
    data = read_csv(path, sep=";")

    features_col = ["Consumption", "Weekday", "Hour", "AVG4D (kWh)", "TempCluster"]
    target_col = "Consumption"

    samples = []
    
    # https://www.youtube.com/watch?v=yF6Jrzz7E5s
    for i in range(0,len(data)-1) :
        
        features = data.loc[i-23:i][features_col]
        target = data.loc[i+1][target_col]
        

        sample = {"features" : features, "target": target}
        
        samples.append(sample)
    

    features_list = [sample["features"] for sample in samples]
    
    # https://www.tensorflow.org/api_docs/python/tf/keras/utils/pad_sequences
    X_train = pad_sequences(features_list[:int(len(samples)*0.85)], padding='pre', dtype='float32')
    X_val= pad_sequences(features_list[int(len(samples)*0.80):int(len(samples)*0.90)], padding='pre', dtype='float32')
    X_test = pad_sequences(features_list[int(len(samples)*0.90):], padding='pre', dtype='float32')

    targets_list = [sample["target"] for sample in samples]

    y_train = array(targets_list[:int(len(samples)*0.85)], dtype='float32')
    y_val = array(targets_list[int(len(samples)*0.80):int(len(samples)*0.90)], dtype='float32')
    y_test = array(targets_list[int(len(samples)*0.90):], dtype='float32')

    return X_train, y_train, X_val, y_val, X_test, y_test



def trainLocalModel() :
    X_train, y_train, X_val, y_val, X_test, y_test = loadData("proto_data.csv")

    local_model = load_model("local_model.keras")
    local_model.compile(optimizer=SGD(learning_rate=0.0001) , loss='mse')
    local_model.fit(x=X_train, y=y_train, validation_data=(X_val, y_val), epochs=5, batch_size = 100)
    local_model.save("local_model.keras")

trainLocalModel()