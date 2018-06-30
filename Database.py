from sqlalchemy.orm import sessionmaker
from DBClasses import Intent, Pattern, Response, engine, Base

DBSession = sessionmaker(bind=engine)

def insertEdit(obj):
    session = DBSession()
    session.add(obj)
    session.commit()
    session.close()

def getIntents():
    session = DBSession()
    intents = session.query(Intent).all()
    session.close()
    return intents