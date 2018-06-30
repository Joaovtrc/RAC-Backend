#JSON
import json
import jsonpickle

#FLASK
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
from flask_cors import CORS, cross_origin

#DB
from DBClasses import Intent, Pattern, Response, IntentSchema, ResponseSchema, PatternSchema
from marshmallow import pprint
from Database import insertEdit, getIntents

#ChatBot&Training
from Training import train
from Chatbot import response as chatBotResponse, classify as chatBotClassify

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/api/ChatBot/Train", methods=["GET", "POST"])
def trainChatbot():
    train()
    return "Ok"

#INTENT

@app.route("/api/Intents",methods=["GET"])
@cross_origin()
def listIntents():
    intents = getIntents()
    schema = IntentSchema(many=True)
    return json.dumps(schema.dump(intents))




@app.route("/api/ChatBot/Response",methods=["POST"])
def responseChatbot():
    question = request.get_json()
    print(question['question'])
    classi = chatBotClassify(question['question'])
    print(classi)  
    return json.dumps(dict(response = chatBotResponse(question['question']), classify = classi))



@app.route("/api/insertIntent",methods=["POST"])
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



if __name__ == "__main__":
    app.run(debug=True)