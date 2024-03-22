from globaldatabase import db 
from flask_login import UserMixin
from ECEbank import ece_questions


class UserDetails(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), unique = True, nullable = False) 
    email = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(255), unique = True, nullable = False)


    def __init__ (self, username, email, password):

       
        self.username = username
        self.email = email
        self.password = password



class Question(db.Model):

    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('Options', backref='questions', lazy=True)



class Options(db.Model):

    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)



db.create_all()


#---Push the questions from ece_questions to the Questions and Options Database---#
for specific_question in ece_questions:

    existing_question = Question.query.filter_by(content=specific_question['content']).first()
    if existing_question:
        question_id = existing_question.id
    else:
        # If the question doesn't exist, add it to the database
        question = Question(content=specific_question['content'])
        db.session.add(question)
        db.session.commit()
        question_id = question.id

    for option in specific_question['options']:
        existing_option = Options.query.filter_by(question_no=question_id, content=option['content']).first()
        if existing_option:
            # Option already exists, no need to add it again
            continue
        else:
             specific_option = Options(question_no=question_id,
                                  letter=option['letter'], 
                                  content=option['content'],
                                  is_correct=option['is_correct'])
             db.session.add(specific_option)
             db.session.commit()

db.session.close()