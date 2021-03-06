#JSON
import json
import jsonpickle
import numpy as np
import random

#FLASK
from flask import Flask, jsonify, render_template, request, redirect, url_for, Response as ResponseHttp
from flask_cors import CORS, cross_origin
from sqlalchemy import exc


#DB
from DBClasses import Intent, Pattern, Response, User, Conversation, IntentSchema, ResponseSchema, PatternSchema, UserSchema, ConversationSchema
from marshmallow import pprint
from Database import insertEdit, getIntents, getSingleIntent, deleteIntent, deleteResponse,deletePattern, getSingleResponse,getIntentByName, getUsers, getSingleUser, addConversation, getAllCvsWithNoAnswer,getAllCvsWithLowClassify,getCvById,getUserByUsername

#ChatBot&Training
from Training import train
from Chatbot import response as chatBotResponse, classify as chatBotClassify, loadData as loadChatbotData

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#Responses
def returnOk():
    message = {
            'status': 200,
            'message': 'Success',
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

#---------------------------------------------------------#

@app.errorhandler(400)
def errorResp(error=None):
    message = {
            'status': 400,
            'message': 'Error: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp

#---------------------------------------------------------#

#Routes
#CHATBOT
@app.route("/api/ChatBot/Train", methods=["GET", "POST"])
@cross_origin()
def trainChatbot():
    train()
    loadChatbotData()
    return returnOk()

#---------------------------------------------------------#

@app.route("/api/ChatBot/Response",methods=["POST"])
@cross_origin()
def responseChatbot():
    question = request.get_json()
    print(question)
    classi = chatBotClassify(question['question'])
    print(len(classi))
    print(question['question'],classi)

    classi_dict={}
    for classification in classi:
        classi_dict[classification[0]] = "{!s}".format(classification[1])
    
    cv = Conversation()
    if(len(classi) != 0):
        classify = classi[0]
        cv.classify = classify[1]

        responseDict = chatBotResponse(question['question'])
        cv.response = Response()
        cv.response = getSingleResponse(responseDict['id'])

        cv.intent = Intent()
        cv.intent = getIntentByName(classify[0])
    else:
        cv.classify = 0

        cv.intent = Intent()
        cv.intent = getIntentByName("NAO_SEI")

        cv.response = random.choice(cv.intent.responses)


    cv.user = getSingleUser(question['idUser'])
    cv.question = question['question']  
  
    addConversation(cv)

    conversationSchema = ConversationSchema()
    return ResponseHttp(response=json.dumps(conversationSchema.dump(cv)),
                    status=200,
                    mimetype="application/json")

    
#---------------------------------------------------------#
#INTENT
@app.route("/api/Intents",methods=["GET"])
@cross_origin()
def listIntents():
    intents = getIntents()
    schema = IntentSchema(many=True)
    return  ResponseHttp(response=json.dumps(schema.dump(intents)),
                    status=200,
                    mimetype="application/json")

                    
@app.route("/api/IntentByName/<string:tagName>",methods=["GET"])
@cross_origin()
def getIntentByTag(tagName):
    intent = getIntentByName(tagName)
    schema = IntentSchema()
    return  ResponseHttp(response=json.dumps(schema.dump(intent)),
                    status=200,
                    mimetype="application/json")

#---------------------------------------------------------#

@app.route("/api/insertIntent",methods=["POST"])
@cross_origin()
def insertIntentAnswersPatterns():
    intents = request.get_json()
    print(intents)
    
    intent = getSingleIntent(intents['id'])

    for resJson in intents['responses']:
        if(resJson['id'] == -1):
            print(resJson)
            res = Response()
            res.response = resJson['response']
            intent.responses.append(res)

    for pattJson in intents['patterns']:
        if(pattJson['id'] == -1):
            patt = Pattern()
            patt.pattern = pattJson['pattern']
            intent.patterns.append(patt)


    try:
        insertEdit(intent)
        return returnOk()

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#


@app.route("/api/insertSingleIntent",methods=["POST"])
@cross_origin()
def insertSingleIntent():
    intentJson = request.get_json()
    print(intentJson)

    intent = Intent()
    intent.tag = intentJson['tag']

    for pattJson in intentJson['patterns']:
        patt = Pattern()
        print(pattJson['pattern'])
        patt.pattern = pattJson['pattern']
        intent.patterns.append(patt)


    try:
        print(intent)
        insertEdit(intent)
        return returnOk()

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/insertIntentJson",methods=["POST"])
@cross_origin()
def insertIntent():
    intents = request.get_json()
    print(intents)
    for intentJson in intents['intents']:
        intent = Intent()
        intent.tag = intentJson['tag']

        for resJson in intentJson['responses']:
            res = Response()
            res.response = resJson
            intent.responses.append(res)

        for pattJson in intentJson['patterns']:
            patt = Pattern()
            patt.pattern = pattJson
            intent.patterns.append(patt)
        
        print(intent)
        insertEdit(intent)
    
    try:
        insertEdit(intent)
        return returnOk()
    except exc.SQLAlchemyError:
        return errorResp() 

#---------------------------------------------------------#
#TODO: IMPLEMENT isDeleted TAG to end conflicts with conversation table while deleting answers and patterns

#Answer/Pattern
@app.route("/api/deleteAnswer/<int:id>",methods=["DELETE"])
@cross_origin()
def delAnswer(id):
    try:
        deleteResponse(id)
        return returnOk()

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/deletePattern/<int:id>",methods=["DELETE"])
@cross_origin()
def delPattern(id):
    try:
        deletePattern(id)
        return returnOk()

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#

#User
@app.route("/api/Users",methods=["GET"])
@cross_origin()
def listUsers():
    print('debug1')
    users = getUsers()
    schema = UserSchema(many=True)
    print('debug2')

    return  ResponseHttp(response=json.dumps(schema.dump(users)),
                    status=200,
                    mimetype="application/json")
         

@app.route("/api/getSingleUser/<int:id>",methods=["GET"])
@cross_origin()
def getUser(id):
    try:
        print('debug1')
        user = getSingleUser(id)
        schema = UserSchema()
        return  ResponseHttp(response=json.dumps(schema.dump(user)),
                    status=200,
                    mimetype="application/json")
        
    except exc.SQLAlchemyError:
        return errorResp()

@app.route("/api/Login",methods=["POST"])
@cross_origin()
def loginUser():
    try:
        userJSON = request.get_json()
        user = getUserByUsername(userJSON['username'])
        print(user)
        if(user != None):
            schema = UserSchema()
            if(user.password == userJSON['password']):
                return  ResponseHttp(response=json.dumps(schema.dump(user)),
                            status=200,
                            mimetype="application/json")
            else:
                return errorResp()
        else:
            return errorResp()
            
    except exc.SQLAlchemyError:
        return errorResp()
#---------------------------------------------------------#

@app.route("/api/insertUser",methods=["POST"])
@cross_origin()
def insertUser():
    try:
        userJSON = request.get_json()
        user = User()
        user.name = userJSON['name']
        user.username = userJSON['username']
        user.password = userJSON['password']
        insertEdit(user)
        return returnOk()

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/getAllCvsWithNoAnswer",methods=["GET"])
@cross_origin()
def getAllCvsWNoAnswer():
    try:
        conversations = getAllCvsWithNoAnswer()
        schema = ConversationSchema(many=True)
        return  ResponseHttp(response=json.dumps(schema.dump(conversations)),
                    status=200,
                    mimetype="application/json")

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/getAllCvsWithLowClassify",methods=["GET"])
@cross_origin()
def getAllCvsWLowClassify():
    try:
        conversations = getAllCvsWithLowClassify()
        schema = ConversationSchema(many=True)
        return  ResponseHttp(response=json.dumps(schema.dump(conversations)),
                    status=200,
                    mimetype="application/json")

    except exc.SQLAlchemyError:
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/curateConversation/<int:idCV>/<int:idIntent>",methods=["POST"])
@cross_origin()
def curateConversation(idCV,idIntent):
    try:
        conversation: Conversation = getCvById(idCV)

        intent: Intent = getSingleIntent(idIntent)
        patt = Pattern()    
        patt.pattern = conversation.question
        intent.patterns.append(patt)
        insertEdit(intent)


        intent = getSingleIntent(idIntent)
        conversation.intent = intent
        addConversation(conversation)

        
        return returnOk()


    except exc.SQLAlchemyError:
        import sys
        print(sys.exc_info())
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/curateConversationWLowClass/<int:idCV>/<int:idIntent>",methods=["POST"])
@cross_origin()
def curateConversationWLowClass(idCV,idIntent):
    try:
        conversation: Conversation = getCvById(idCV)
        conversation.classify = 0.31
        intent: Intent = getSingleIntent(idIntent)
        patt = Pattern()    
        patt.pattern = conversation.question
        intent.patterns.append(patt)
        insertEdit(intent)


        intent = getSingleIntent(idIntent)
        conversation.intent = intent
        addConversation(conversation)

        
        return returnOk()


    except exc.SQLAlchemyError:
        import sys
        print(sys.exc_info())
        return errorResp()

#---------------------------------------------------------#

@app.route("/api/curateConversationWCorrectAnswer/<int:idCV>",methods=["POST"])
@cross_origin()
def curateConversationWCorrectAnswer(idCV):
    try:
        conversation: Conversation = getCvById(idCV)
        conversation.classify = 0.31
        intent: Intent = conversation.intent
        patt = Pattern()    
        patt.pattern = conversation.question
        intent.patterns.append(patt)
        insertEdit(intent)

        addConversation(conversation)

        
        return returnOk()


    except exc.SQLAlchemyError:
        import sys
        print(sys.exc_info())
        return errorResp()

#---------------------------------------------------------#

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)