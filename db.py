from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    topics = relationship('Topic', backref='Language', lazy='dynamic')

    def __repr__(self):
        return '<Language: {}>'.format(self.name)


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    lang_id = Column(Integer, ForeignKey('languages.id'))
    questions = relationship('Question', backref='topic', lazy='dynamic')

    def __repr__(self):
        return '<Topic: {}>'.format(self.title)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String(250), nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'))

    def __repr__(self):
        return '<Question: {}>'.format(self.text[0:20])


engine = create_engine('sqlite:///db.sqlite',
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)

_session = sessionmaker(bind=engine)
session = _session()
