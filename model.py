# Package for tensorflow layers
from tensorflow.keras.layers import LSTM, Dense, Input

# Package for creating model objects
from tensorflow.keras.models import Sequential


# Function for creating the project model architecture
def getmodel() :
    print("Executing function 'createModel'...")

    # Creating model object
    print("**Creating a Sequential model object**")
    model = Sequential()
    
    # Adding an Input layer
    print("**Adding an Input layer to the model object**")
    model.add(Input(shape = (24, 5)))

    # Adding an LSTM layer
    print("**Adding an LSTM layer to the model object**")
    model.add(LSTM(32, return_sequences=True))

    # Adding an LSTM layer
    print("**Adding an LSTM layer to the model object**")
    model.add(LSTM(16))

    # Adding a Dense layer
    print("**Adding a Dense layer to the model object**")
    model.add(Dense(1))
    
    # Returning model object
    print("**Returning the model object**")
    return model



# Function for saving the model object 
def createModel(path) :
    print("Executing function 'createModel'...")
    
    # Getting model object completed
    print("*Getting model object *via function* *")
    model = getmodel()
    
    # Saving model object
    print(f"*Saving model object at the path {path}*")
    model.save(path)
    
    # Returning path of the save
    print(f"returning path")
    return path