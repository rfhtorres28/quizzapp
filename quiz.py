from flask import Flask, request, render_template, url_for, flash, redirect, get_flashed_messages, make_response, jsonify
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt 
from flask_login import current_user, LoginManager, login_user, logout_user, login_required 
from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


#-----Initializing the flask app-------#
        
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '582ea1bb8309ccf43fd65b39d593a6a6'
bcrypt = Bcrypt(app)


#------ Creating a user database -------#

username='root'
password= 'Toootsie@1430'
port = '3306'
host = 'localhost'
database_name= 'quiz'


#-----Initializing the Database-------#

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}'
db = SQLAlchemy(app)


class UserDetails(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), unique = True, nullable = False) 
    email = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(255), unique = True, nullable = False)


    def __repr__(self):

        return f"User('{self.username}', '{self.email}', '{self.password}')"



class Question(db.Model):

    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('Options', backref='questions', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class Options(db.Model):

    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"




class QuizForm(FlaskForm):
    user_id = HiddenField()

def create_dynamic_fields(questions):
    
    for i, question in enumerate(questions, start=1):
        choices = [(option['letter'], option['content']) for option in question['options']]
        field_name = f'q{i}'
        field_label = question['content']
        setattr(QuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))


qn = Question.query.all()
opn = Options.query.all()
ece_questions = [{"id":question.id, "content":question.content,
                "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]

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
        
        elif len(username.data) > 10:
            flash('Username has a limit of 10 characters only', 'error')
            raise ValidationError('Username exceeds maximum limit of 10 characters only')
        

    def validate_email(self, email):
        print("Validating username:", email)
        email = UserDetails.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('Email already exists. Please choose other email')




#----- Creating the Login Form ------#
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    
          







#----- Initializing Login Manager ------#
login_manager = LoginManager(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return UserDetails.query.get(int(user_id))


#----- Creating the endpoint routes ------#
@app.route('/home', methods=['GET'])
def home():
    return render_template('homev1.html')



@app.route('/member-register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
        
    if request.method == 'POST':
        if form.validate_on_submit():
          hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
          user = UserDetails(username=form.username.data, email=form.email.data, password=hashed_password)
          db.session.add(user)
          db.session.commit()
          flash('Your account has been sucessfully created! You may now login', 'success')
        
          return redirect(url_for('login')) # return here ensures that the url for home page is sent back (return back) to the clients browser


    
    return render_template('register_quiz.html', form=form)
        


@app.route('/member-login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    messages = get_flashed_messages()
    if form.validate_on_submit():
        user = UserDetails.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user) # Get the state of the user that is currently login, so it means that if a user logs in, it is stored in the login_user()
            return redirect(url_for('courses'))
        

        else:
            flash('Login unsuccesful, Please try again')
            return redirect(url_for('login'))
        
    
    return render_template('login_quiz.html', form=form, messages=messages)



@app.route("/courses")
def courses():
    return render_template('homev2.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.errorhandler(404)
def page_not_found(error):
    if request.path.endswith('.html'):
        return render_template('404.html'), 404
    
    else:
        return "Page Not Found", 404 


class Electronics(Resource):
   
   @login_required
   def get(self):
       if not current_user.is_authenticated:
            return redirect(url_for('login'))
       
       form = QuizForm() 
       return make_response(render_template('quiz.html', questions=ece_questions, form=form))
       
   
   def post(self):
            
            form = QuizForm() 
            no_correct_answer = 0
            correct_answers = []
            total_questions = len(ece_questions)
            user_responses = {}
            form_data = {}

            if form.validate_on_submit():
                form_data = request.form.to_dict()  
    
            for question in ece_questions: 
                user_response = form_data.get(f'q{question["id"]}') 
                correct_response = [x for x in question['options'] if x['is_correct']==True] 
                correct_answers.append(correct_response) 
                user_responses[f'q{question["id"]}'] = user_response
                if user_response == correct_response[0]["letter"]:
                    no_correct_answer += 1

  
            score_percentage = no_correct_answer/total_questions*100
            score_percentage = round(score_percentage, 2)
         
            return make_response(render_template('result1.html', form=form, score_percentage=score_percentage,
                                  no_correct_answer=no_correct_answer, total_questions=total_questions, correct_answers=correct_answers))
   
   
       


api.add_resource(Electronics, '/courses/electronics')


@app.route('/courses/electronics/answers')
@login_required #Safety feature so that user that is not authenticated cant access the correct answers
def answers():
    correct_answers = []
    if current_user.is_authenticated:
        for question in ece_questions:
            correct_response = [x for x in question['options'] if x['is_correct']==True] 
            correct_answers.append(correct_response) 
    
    return render_template('correct_answers.html', correct_answers=correct_answers)





if __name__ == '__main__':
    app.run(debug=True)


# render_template typically returns an html string so use make_response() to ensure 