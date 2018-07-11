#JSON
import json
import jsonpickle

#FLASK
from flask import Flask, render_template, request, redirect, url_for, Response
from flask import jsonify
from flask_cors import CORS, cross_origin
from sqlalchemy import exc


#DB
from DBClasses import Intent, Pattern, Response, IntentSchema, ResponseSchema, PatternSchema
from marshmallow import pprint
from Database import insertEdit, getIntents, getSingleIntent, deleteIntent, deleteAnswer

#ChatBot&Training
from Training import train
from Chatbot import response as chatBotResponse, classify as chatBotClassify

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

@app.errorhandler(400)
def errorResp(error=None):
    message = {
            'status': 400,
            'message': 'Error: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp


#Routes
@app.route("/api/ChatBot/Train", methods=["GET", "POST"])
@cross_origin()
def trainChatbot():
    train()

    #IMPLEMENTAR RESPOSTA COM CONTENT TYPE CERTO!!!!!!!!!!!!!!
    return "Ok"

#INTENT

@app.route("/api/Intents",methods=["GET"])
@cross_origin()
def listIntents():
    intents = getIntents()
    schema = IntentSchema(many=True)
    return json.dumps(schema.dump(intents))




@app.route("/api/ChatBot/Response",methods=["POST"])
@cross_origin()
def responseChatbot():
    question = request.get_json()
    print(question['question'])
    classi = chatBotClassify(question['question'])
    print(classi)  
    return json.dumps(dict(response = chatBotResponse(question['question'])))



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
    
@app.route("/api/insertIntentJson",methods=["POST"])
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
    
    return "Ok" 

@app.route("/api/deleteAnswer/<int:id>",methods=["DELETE"])
@cross_origin()
def delAnswer(id):
    try:
        deleteAnswer(id)
        return returnOk()

    except exc.SQLAlchemyError:
        return errorResp()

if __name__ == "__main__":
    app.run(debug=True)

