# import Section
import fitz
import docx
import numpy as np
import pandas as pd
from tensorflow  import keras
#from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import json




#from trainedModel import trainedModel
from trainedModel  import trainedModelAndBagOfWords

#from AbstractParse.trainedModel import trainedModel
max_length = 100
trunc_type = 'post'
padding_type = 'post'





#inputFilename is the path of pdf which needs to be processed
#folderName is the folder where all the Docx file of the abstract would be placed
# textAndCharacteristics would return text  and the characteristcs present in the paragraph

def textAndCharacteristics(inputFilename,filenameDocx):
    docObject = fitz.open(inputFilename)
    pageNumber = 0
    text = []
    characterists = []
    for page in docObject:
        pageNumber += 1 
        blocks = page.getText("dict")["blocks"]
        for b in blocks:
            paragraph = ""
            character = []
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  
                        ch = []
                        ch.append(int(s["size"]))
                        ch.append(s["font"])
                        ch.append(s["color"])
                        paragraph = paragraph + (s["text"]) + " "
                        
                        #print(paragraph)
                        #print(character)
                        character.append(ch)
                        
                characterists.append(character)            
                text.append(paragraph)
            
    return text, characterists, docObject
                    
def removeRedundantCharacterists(characterists):
    uniqueCharacterists = []
    for i in range(len(characterists)):
        paragraphCharacterists =[]
        for k in range(len(characterists[i])):      
            if(characterists[i][k] not in paragraphCharacterists):
                paragraphCharacterists.append(characterists[i][k])
        uniqueCharacterists.append(paragraphCharacterists)
    return uniqueCharacterists



#input is the paragraph in each index of the list named text obtained from pyMupdf



def newPdfGetTextLabelsAndTextIndex(text,characterists,modelLocation,TokenizerLocation):
    #Loading the required model and the tokenizer
    model , tokenizer =trainedModelAndBagOfWords(modelLocation,TokenizerLocation)
    output =["Title", "Author", "Affiliation" , "Abstract", "Noise", "Image" ,"ID's"]
    
    
    text_1 = tokenizer.texts_to_sequences(text)
    text_2 = keras.preprocessing.sequence.pad_sequences(text_1, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    #print(text1) # prints the converted form of text to number
    #print(text2) #prints the padded sequences if the sequences length is small is paddes the additional value
    
    
    #model prediction
    textClass =model.predict(text_2)
    
    #print(textClass)
    textIndex = []
    textLabels = []
    for i in range(len(textClass)):
        textIndex.append(np.argmax(textClass[i]))
        textLabels.append(output[np.argmax(textClass[i])])
        
        
    #prints the paragraph and Characteristcs and Classification class
    '''
    for i in range(len(text)):
        print(text[i])
        print(textLabels[i])
        print(characterists[i])
        print()
        print()
    '''
    return  textLabels, textIndex 


def classGrouping(textIndex, textLabels, text, characteristics):
    
    abstract = []
    title = []
    author = []
    affliation = []
    noise = []
    ids = []
    
    for i in range(len(text)):
        #print(text[i])
        #print(textLabels[i])
        
        if(textIndex [i] == 0):
            title.append(characteristics[i])
        elif(textIndex [i] == 1):
            author.append(characteristics[i])
        elif(textIndex [i] == 2):
            affliation.append(characteristics[i])
        elif(textIndex [i] == 3):
            abstract.append(characteristics[i])
        elif(textIndex [i] == 4):
            noise.append(characteristics[i])
        elif(textIndex [i] == 6):
            ids.append(characteristics[i])
    
    return title, author, affliation, abstract, noise, ids   



def clusterFormation(CLASS , NAME):
    #pass each grouped class as an input their respective clusters with characteristics  would be formed 
    cluster = {}
    for i in range(len(CLASS)):
        for j in range(len(CLASS[i])):
            value =str(CLASS[i][j][0])+","+CLASS[i][j][1]+","+str(CLASS[i][j][2])
            #print(value)
            if(value not in cluster):
                cluster[value] = 1
            if(value in cluster):
                cluster[value] += 1
        
    ''' 
    print(NAME + "cluster")
    print(sorted(cluster.items(), key=lambda x: x[1], reverse=True))
    print()
    '''
    return cluster

'''
def removeOtherClassCharacteristics(CLASS, otherCharacteristics):
    maxValue =0
    characteristics = ""
    for i in CLASS:
        if(CLASS[i] > maxValue):
            maxValue = CLASS[i]
            characteristics = i
    otherCharacteristics.append(characteristics)
    return otherCharacteristics

'''

def removeOtherClassCharacteristics(CLASS, otherCharacteristics):
    count = 0
    characteristics = ""
    for i in CLASS:
        count += CLASS[i]
    
    if (count == 0):
        return otherCharacteristics
    
    for i in CLASS:
        CLASS[i] = (CLASS[i]/count) * 100
    
    for i in CLASS:
        #print(CLASS[i])
        if(CLASS[i] >= 50):
            characteristics = i
    otherCharacteristics.append(characteristics)
    return otherCharacteristics




def uniqueTitleCharacteristics(titleCluster , otherCharacteristics):
    maxValue = 0
    characteristics = ""
    for i in titleCluster:
        if(titleCluster[i] > maxValue) and (i not in otherCharacteristics):
            maxValue = titleCluster[i]
            characteristics = i
    characteristics = characteristics.split(",")
    characteristics[0] =int(characteristics[0])
    characteristics[2] =int(characteristics[2])
    fontSize = int(characteristics[0])
    fontFamily = characteristics[1]
    colour  = int(characteristics[2])
    return fontSize , fontFamily , colour , characteristics


