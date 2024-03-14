from flask import Flask, request, render_template, url_for, flash, jsonify, redirect, session
from ECEbank import ece_questions
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import  UserMixin
from ECEbank import ece_questions
from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError


#-----Initializing the flask app-------#
        
app = Flask(__name__)
app.config['SECRET_KEY'] = '582ea1bb8309ccf43fd65b39d593a6a6'
bcrypt = Bcrypt(app)


#------ Creating a user database -------#

username='root'
password= 'Toootsie@1430'
port = '3306'
host = 'localhost'
database_name= 'user'

#-----Initializing the Database-------#

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}'
db = SQLAlchemy(app)

class UserDetails(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), unique = True, nullable = False) 
    email = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(255), unique = True, nullable = False)


    def __init__ (self, username, email, password):

       
        self.username = username
        self.email = email
        self.password = password





#----- Creating a Quiz Form ------#
class QuizForm(FlaskForm):
    user_id = HiddenField()

def create_dynamic_fields(questions):
    for i, question in enumerate(questions, start=1):
        choices = [(option['letter'], option['content']) for option in question['options']]
        field_name = f'q{i}'
        field_label = question['content']
        setattr(QuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))

create_dynamic_fields(ece_questions)


#----- Creating the Registration Form ------#
class RegistrationForm(FlaskForm):
    
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    
    def validate_username(self, username):
        print("Validating username:", username)
        user = UserDetails.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username already exists. Please choose other username')
        

    def validate_email(self, email):
        print("Validating username:", email)
        email = UserDetails.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('Email already exists. Please choose other email')







#----- Creating the endpoint routes ------#
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
          hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
          user = UserDetails(username=form.username.data, email=form.email.data, password=hashed_password)
          db.session.add(user)
          db.session.commit()
          flash('Your account has been sucessfully created!', 'success')
        
          return redirect(url_for('register')) # return here ensures that the url for home page is sent back (return back) to the clients browser



    return render_template('register_quiz.html', form=form)
        



















@app.route('/electronics', methods=['GET', 'POST'])
def elecs():
     
     no_correct_answer = 0
     correct_answers = []
     total_questions = len(ece_questions)
     user_responses = {}
     form = QuizForm() 
     
     

     if request.method == 'POST':
       if form.validate_on_submit():
         form_data = request.form.to_dict()
        
          
         for question in ece_questions: # loop through the list of dictionary questions
               user_response = form_data.get(f'q{question["id"]}') # return the value pair from the form data 
               correct_response = [x for x in question['options'] if x['is_correct']==True] # this return the correct answer for each question
               correct_answers.append(correct_response) # or correct_letters.append(correct_response[0] if correct_response else None)
               user_responses[f'q{question["id"]}'] = user_response
               if user_response == correct_response[0]["letter"]:
                   no_correct_answer += 1
               
           
         
         score_percentage = no_correct_answer/total_questions*100
         score_percentage = round(score_percentage, 2)
         
         return jsonify(form_data)
            
       
  
     
     return render_template('quiz.html', questions=ece_questions, form=form)
        




if __name__ == '__main__':
    app.run(debug=True)