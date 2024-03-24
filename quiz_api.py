from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from ECEbank import ece_questions


app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)


username='root'
password= 'Toootsie@1430'
port = '3306'
host = 'localhost'
database_name= 'quiz'


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}'


class Question(db.Model): 

    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('Options', backref='questions', lazy=True)



class Options(db.Model):  

    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_no = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)








class QuizQuestions(Resource):

    def get(self):
        qn = Question.query.all()
        opn = Options.query.all()
        
        ece_questions = [{"id":question.id, "content":question.content,
                        "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]
     

        return ece_questions        
            

    
        
       





api.add_resource(QuizQuestions, '/questions')






if __name__ == "__main__": 
    app.run(debug=True)