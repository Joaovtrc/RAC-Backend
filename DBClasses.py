import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
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


engine = create_engine('sqlite:///rac_database.db')


Base.metadata.create_all(engine)