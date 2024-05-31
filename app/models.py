from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import UnicodeText
from sqlalchemy.ext.hybrid import hybrid_property
from . import db


class UserDetails(db.Model, UserMixin):

    __tablename__ = 'userdetails'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique = True) 
    firstname = db.Column(db.String(255)) 
    lastname = db.Column(db.String(255)) 
    image_file = db.Column(db.String(255), nullable=False, default='default.png')
    email = db.Column(db.String(255), unique = True)
    password = db.Column(db.String(255), unique = True)
    date_of_birth = db.Column(db.Date)
    country = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    instagram_link = db.Column(db.String(255))
    facebook_link = db.Column(db.String(255))
    bio = db.Column(UnicodeText, nullable=True, default='')

    def __repr__(self):

        return f"User('{self.username}', '{self.email}', '{self.password}')"



class ElecsQuestions(db.Model):

    __tablename__ = 'elecsquestions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('ElecsOptions', backref='elecsquestions', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class ElecsOptions(db.Model):

    __tablename__ = 'elecsoptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_no = db.Column(db.Integer, db.ForeignKey('elecsquestions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"


class CommsQuestions(db.Model):

    __tablename__ = 'commsquestions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('CommsOptions', backref='commsquestions', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class CommsOptions(db.Model):

    __tablename__ = 'commsoptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_no = db.Column(db.Integer, db.ForeignKey('commsquestions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"

class MathQuestions(db.Model):

    __tablename__ = 'mathquestions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('MathOptions', backref='mathquestions', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class MathOptions(db.Model):

    __tablename__ = 'mathoptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_no = db.Column(db.Integer, db.ForeignKey('mathquestions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"
    

class GEASQuestions(db.Model):

    __tablename__ = 'geasquestions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('GEASOptions', backref='geasquestions', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class GEASOptions(db.Model):

    __tablename__ = 'geasoptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_no = db.Column(db.Integer, db.ForeignKey('geasquestions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"


class UserResult(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    session_id = db.Column(db.String(50), nullable=False)
    score_percentage = db.Column(db.String(5))
    no_correct_answer = db.Column(db.String(5))
    posted_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    latest_login = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    profile_pic = db.Column(db.String(255), nullable=True)
    difference = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255))

    @hybrid_property
    def time_difference(self):
        return self.latest_login - self.posted_time


class UserPost(db.Model):

    __tablename__ = 'userpost'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'), nullable=False)
    post = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    session_id = db.Column(db.String(50), nullable=False)
    posted_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    latest_login = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    profile_pic = db.Column(db.String(255), nullable=True)
    difference = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(255))

    @hybrid_property
    def time_difference(self):
        return self.latest_login - self.posted_time
