from sqlalchemy.orm import sessionmaker
from DBClasses import Intent, Pattern, Response, engine, Base

DBSession = sessionmaker(bind=engine)

def insertEdit(obj):
    session = DBSession()
    session.add(obj)
    session.commit()
    session.close()


#Intent
def getIntents():
    session = DBSession()
    intents = session.query(Intent).all()
    session.close()
    return intents

def getSingleIntent(id):
    session = DBSession()
    intent = session.query(Intent).filter_by(id=id).first()
    session.close()
    return intent

def deleteIntent(id):
    session = DBSession()
    intent = session.query(Intent).filter_by(id=id).first()
    session.delete(intent)
    session.commit()
    session.close()

#Answer

def deleteAnswer(id):
    session = DBSession()
    response = session.query(Response).filter_by(id=id).first()
    session.delete(response)
    session.commit()
    session.close()
