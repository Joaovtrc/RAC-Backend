import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import json
import nltk
from nltk.stem.lancaster import LancasterStemmer

from Database import getIntents

from DBClasses import Intent, Pattern, Response, IntentSchema, ResponseSchema, PatternSchema

from marshmallow import pprint

#inicia tflearn com 0.1 da memória da GPU
tf.reset_default_graph()
tflearn.init_graph(gpu_memory_fraction=0.1)

#inicia o stemmer em PTBR
stemmer = nltk.stem.RSLPStemmer()

#Carrega os dados que a Classe Training.py criou e colocou no arquivo training_data.
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# Carrega as intents do banco de dados
schema = IntentSchema(many=True)
intents = schema.dump(getIntents())


#Constrói a rede neural
with tf.device('/gpu:0'):
    net = tflearn.input_data(shape=[None, len(train_x[0])])
    #Número de nós da rede
   # net = tflearn.fully_connected(net, 16)
    net = tflearn.fully_connected(net, 16) #inicia o nó da rede com 16 neurônios
    net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
    net = tflearn.regression(net)

    #Define o model e diz qual o diretório os logs da rede ficam
    model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

    # Carrega o modelo feito pelo treinamento
    model.load('./model.tflearn')


def clean_up_sentence(sentence):
    # Tokeniza as palavras(separa cada palavra em um array)
    sentence_words = nltk.word_tokenize(sentence)
    # Stemma as palavras e as retorna
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# Retorna uma lista de 0 e 1 se a palvavra na sentença está dentro dos dados carregados
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))


# Instancia o contexto das conversas
context = {}

ERROR_THRESHOLD = 0.25
def classify(sentence):
    # Gera probabilidades com o model gerado pelo treinamento
    with tf.device('/gpu:0'):
        results = model.predict([bow(sentence, words)])[0]
    # Filtra todas com menos de 0.25
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # Ordena do maior pro menor
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # Retorna um tuple com a intent e a probabilidade
    return return_list

def response(sentence, userID='123', show_details=False):
    intents = schema.dump(getIntents())
    results = classify(sentence)
    # Se existe classificação procura e retorna uma resposta dentro da maior
    if results:
        while results:
            for i in intents:
                # Encontra qual a intent certa
                if i['tag'] == results[0][0]:
                    # Seta o contexto da conversa com o id do usuário
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # Checa se a intent é contextual e retorna uma resposta aleatória da intent
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        response = random.choice(i['responses'])
                        return response

            results.pop(0)