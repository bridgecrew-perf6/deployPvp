#import Section
import json
import tensorflow as tf

# model location 'C:/Users/darshanRaghunath/tfModel.h5'
# Tokenizer Location 'C:/Users/darshanRaghunath/tokenizer.json'

def trainedModelAndBagOfWords(modelLocation,TokenizerLocation):
    
    model = tf.keras.models.load_model(modelLocation)

    with open(TokenizerLocation) as json_file:
        json_string = json.load(json_file)
    tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(json_string)
    return model,tokenizer





#model, tokenizer = trainedModelAndBagOfWords('tfModel.h5','tokenizer.json')

