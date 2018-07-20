import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from marshmallow import Schema, fields, pprint

Base = declarative_base()
    
class Intent(Base):
    __tablename__ = 'intents'
    id = Column(Integer, primary_key = True,autoincrement=True)
    tag = Column(String(50), nullable = False)
    context_filter = Column(String(50), nullable = True)
    context_set = Column(String(50), nullable = True)
    patterns = relationship('Pattern',backref ='intents', lazy='subquery')
    responses = relationship('Response',backref='intents', lazy='subquery')

class Pattern(Base):
    __tablename__ = 'patterns'
    id = Column(Integer, primary_key=True,autoincrement=True)
    pattern = Column(String(300), nullable=False)
    intent_id = Column(Integer, ForeignKey('intents.id'))

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True,autoincrement=True)
    response = Column(String(500), nullable=False)
    intent_id = Column(Integer, ForeignKey('intents.id'))

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    username = Column(String(20), nullable=False)
    password = Column(String(30), nullable=False)
    name = Column(String(300), nullable=False)
    conversations = relationship('Conversation',backref ='users', lazy='subquery')

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True,autoincrement=True)
    question = Column(String(500), nullable=False)
    classify = Column(Float(5))
    date = Column(DateTime, default=datetime.datetime.now())

    response_id = Column(Integer, ForeignKey('responses.id'))
    response = relationship('Response', lazy='subquery')

    intent_id = Column(Integer, ForeignKey('intents.id'))
    intent = relationship('Intent', lazy='subquery')

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', lazy='subquery')



    



##SCHEMAS

class PatternSchema(Schema):
    id = fields.Integer()
    pattern = fields.String()
    intent_id = fields.Integer()

class ResponseSchema(Schema):
    id = fields.Integer()
    response = fields.String()
    intent_id = fields.Integer()

class IntentSchema(Schema):
    id = fields.Integer()
    tag = fields.String()
    context_filter = fields.String()
    context_set = fields.String()
    patterns = fields.Nested(PatternSchema(), many=True)
    responses = fields.Nested(ResponseSchema(), many=True)

class ConversationSchema(Schema):
    id = fields.Integer()
    question = fields.String()
    date = fields.Date(dump_only=True)
    user = fields.Nested('UserSchema')
    classify = fields.Float()
    intent = fields.Nested(IntentSchema(only=('tag', 'id')))
    response = fields.Nested(ResponseSchema())

class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    username = fields.String()
    password = fields.String(load_only=True)
    conversations = fields.Nested(ConversationSchema, many=True, exclude=('user',))




engine = create_engine('sqlite:///rac_database.db')


Base.metadata.create_all(engine)