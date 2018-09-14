import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = nltk.stem.RSLPStemmer()

import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import json

#DB
from Database import getIntents
from DBClasses import Intent, Pattern, Response, IntentSchema, ResponseSchema, PatternSchema

train_x = list()
train_y = list()
val_x = list()
val_y = list()

words = []
docsTrain = []
docsVal = []
classesTrain = []
classesVal = []

def train():
    print('debug1')
    #Carrega as intents do banco de dados
    schema = IntentSchema(many=True)
    intents = schema.dump(getIntents())
    for intent in intents:
        if(intent["tag"] == "NAO_SEI"):
            intents.remove(intent)

    print(intents)

    with open('validation_set.json', encoding="utf8") as json_data:
        validation_set = json.load(json_data)

    prepareWordsArray(intents, validation_set)
    
    prepareTrainingSet()
    prepareValidatitonSet()

    global val_x
    global val_y
    global train_x
    global train_y

    #inicia tflearn com 0.1 da memória da GPU
    tf.reset_default_graph()
    tflearn.init_graph(gpu_memory_fraction=0.7)

    #Constrói a rede neural
    with tf.device('/job:localhost/replica:0/task:0/device:GPU:0'):
        net = tflearn.input_data(shape=[None, len(train_x[0])])

        #Número de nós da rede
        #net = tflearn.fully_connected(net, 16)
        net = tflearn.fully_connected(net, 16) #inicia o nó da rede com 16 neurônios
        net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
        
        net = tflearn.regression(net)

        #Define o model e diz qual o diretório os logs da rede ficam
        model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
        # Começa o treinamento e salva o treinamento
      
        
        model.fit(train_x, train_y, n_epoch=1000, snapshot_step=100, snapshot_epoch=False, validation_set=(val_x, val_y), show_metric=True)
        model.save('model.tflearn')

        #Gera um arquivo com os dados usados no treinamento
        pickle.dump( {'words':words, 'classes':classesTrain, 'train_x':train_x, 'train_y':train_y}, open( "training_data", "wb" ) )
        

def prepareWordsArray(trainingSet, validationSet):
    #Lista de palavras a serem ignoradas
    ignore_words = nltk.corpus.stopwords.words('portuguese')
    global words
    global docsTrain
    global classesTrain
    global docsVal
    global classesVal

    for intent in validationSet['intents']:
        for pattern in intent['patterns']:
            # tokenize each word in the sentence
            w = nltk.word_tokenize(pattern)
            # add to our words list
          
            
            words.extend(w)
            # add to documents in our corpus
            docsVal.append((w, intent['tag']))
            # add to our classes list
            if intent['tag'] not in classesVal:
                classesVal.append(intent['tag'])

    for intent in trainingSet:
        for pattern in intent['patterns']:
            print(pattern['pattern'])
            # Tokeniza as palavras(separa cada palavra em um array)
            w = nltk.word_tokenize(pattern['pattern'])
            # adiciona na lista de palavras
            words.extend(w)
            # adiciona nos documentos
            docsTrain.append((w, intent['tag']))
            # adiciona nas classes se não existir
            if intent['tag'] not in classesTrain:
                classesTrain.append(intent['tag'])

    # stem and lower each word and remove duplicates
    words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))

    print("words", words)

def prepareValidatitonSet():
    global words
    global docsVal
    global classesVal

    # remove duplicates
    classesVal = sorted(list(set(classesVal)))

    print (len(docsVal), "documentsVal", docsVal)
    print (len(classesVal), "classesVal", classesVal)
    print (len(words), "unique stemmed words", words)

    # create our training data
    validation = []
    output = []
    # create an empty array for our output
    output_empty = [0] * len(classesVal)

    # training set, bag of words for each sentence
    for docV in docsVal:
        # initialize our bag of words
        bagVal = []
        # list of tokenized words for the pattern
        pattern_words = docV[0]
        # stem each word
        pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
        # create our bag of words array
        for w in words:
            bagVal.append(1) if w in pattern_words else bagVal.append(0)

        # output is a '0' for each tag and '1' for current tag
        output_row = list(output_empty)
        output_row[classesVal.index(docV[1])] = 1

        validation.append([bagVal, output_row])

    # shuffle our features and turn into np.array
    random.shuffle(validation)
    validation = np.array(validation)


    global val_x 
    global val_y
    val_x = list(validation[:,0])
    val_y = list(validation[:,1])


def prepareTrainingSet():
    global words
    global docsTrain
    global classesTrain

    # remove duplicates
    classesTrain = sorted(list(set(classesTrain)))

    print (len(docsTrain), "docsTrain", docsTrain)
    print (len(classesTrain), "classesTrain", classesTrain)
    print (len(words), "unique stemmed words", words)

    # create our training data
    training = []
    output = []
    # create an empty array for our output
    output_empty = [0] * len(classesTrain)

    # training set, bag of words for each sentence
    for doc in docsTrain:
        # initialize our bag of words
        bag = []
        # list of tokenized words for the pattern
        pattern_words = doc[0]
        # stem each word
        pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
        # create our bag of words array
        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)

        # output is a '0' for each tag and '1' for current tag
        output_row = list(output_empty)
        output_row[classesTrain.index(doc[1])] = 1
        training.append([bag, output_row])
    # shuffle our features and turn into np.array
    random.shuffle(training)
    training = np.array(training)


    global train_x 
    global train_y
    train_x = list(training[:,0])
    train_y = list(training[:,1])


#train()