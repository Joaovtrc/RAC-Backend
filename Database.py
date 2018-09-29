from sqlalchemy.orm import sessionmaker
from DBClasses import Intent, Pattern, Response, User, Conversation,engine, Base

DBSession = sessionmaker(bind=engine)
session = DBSession()

def insertEdit(obj):
    session.add(obj)
    session.commit()
    session.close()


#Intent
def getIntents():
    intents = session.query(Intent).all()
    session.close()
    return intents

def getSingleIntent(id):
    intent = session.query(Intent).filter_by(id=id).first()
    session.close()
    return intent

def getIntentByName(name):
    intent = session.query(Intent).filter_by(tag=name).first()
    session.close()
    return intent

def deleteIntent(id):
    intent = session.query(Intent).filter_by(id=id).first()
    session.delete(intent)
    session.commit()
    session.close()

#Answer

def getSingleResponse(id):
    response = session.query(Response).filter_by(id=id).first()
    session.close()
    return response

def deleteResponse(id):
    response = session.query(Response).filter_by(id=id).first()
    session.delete(response)
    session.commit()
    session.close()

#Pattern
def getSinglePattern(id):
    pattern = session.query(Pattern).filter_by(id=id).first()
    session.close()
    return pattern

def deletePattern(id):
    pattern = session.query(Pattern).filter_by(id=id).first()
    session.delete(pattern)
    session.commit()
    session.close()


#Conversation

def addConversation(cv):
    session.merge(cv)
    session.commit()
    session.close()

def getCvById(id):
    cvs = session.query(Conversation).filter_by(id=id).first()
    session.close()
    return cvs

def getAllCvsWithNoAnswer():
    cvs = session.query(Conversation).join(Intent).filter(Intent.tag=='NAO_SEI').all()
    session.close()
    return cvs

#User

def getUsers():
    users = session.query(User).all()
    session.close()
    return users

def getSingleUser(id):
    user = session.query(User).filter_by(id=id).first()
    session.close()
    return user

def getUserByUsername(username):
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user