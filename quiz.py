from flask import Flask, request, render_template, url_for, flash, redirect, get_flashed_messages, make_response, jsonify
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt 
from flask_login import current_user, LoginManager, login_user, logout_user, login_required 
from flask_wtf import FlaskForm
from wtforms import RadioField, HiddenField, StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from email_validator import validate_email, EmailNotValidError


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
database_name= 'quizapp'


#-----Initializing the Database-------#

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}'
db = SQLAlchemy(app)



class UserDetails(db.Model, UserMixin):

    __tablename__ = 'userdetails'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique = True) 
    firstname = db.Column(db.String(255)) 
    lastname = db.Column(db.String(255)) 
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    email = db.Column(db.String(255), unique = True)
    password = db.Column(db.String(255), unique = True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    instagram_link = db.Column(db.String(255))
    facebook_link = db.Column(db.String(255))

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
        choices = [(option['letter'], option['content']) for option in question['options']] # a list of tuples, elements can be access same as a list
        field_name = f'Question {i}.'
        field_label = question['content']
        setattr(QuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))


qn = Question.query.all()
opn = Options.query.all()
ece_questions = [{"id":question.id, "content":question.content,
                "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]

create_dynamic_fields(ece_questions)




class RegistrationForm(FlaskForm):
    
    firstname = StringField('Firstname', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Lastname', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')
    
    
    def validate_username(self, username):
     
        user = UserDetails.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('Username already exists. Please choose other username')
        
        elif len(username.data) > 10:
            flash('Username has a limit of 10 characters only', 'error')
            raise ValidationError('Username exceeds maximum limit of 10 characters only')
        

    def validate_email(self, email):
      
        email = UserDetails.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('Email already exists. Please choose other email')



class ProfileForm(FlaskForm):

    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    instagram_username = StringField('Instagram', validators=[DataRequired()])
    facebook_username = StringField('Facebook', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth')
    submit = SubmitField('Finish')



 
   
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateInformation(FlaskForm):
    firstname_update = StringField('Firstname', validators=[DataRequired()])
    lastname_update = StringField('Lastname', validators=[DataRequired()])
    username_update = StringField('Username', validators=[DataRequired()])
    email_update = StringField('Email', validators=[DataRequired(), Email()])
    gender_update = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    ig_username_update = StringField('Instagram', validators=[DataRequired()])
    fb_username_update = StringField('Facebook', validators=[DataRequired()])
    date_of_birth_update = DateField('Date of Birth')
    submit = SubmitField('Update')


    def validate_username(self, username_update):

        user = UserDetails.query.filter_by(username=username_update.data).first()

        if user:
            raise ValidationError('Username is already taken')
        





#----- Initializing Login Manager ------#
login_manager = LoginManager(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return UserDetails.query.get(int(user_id))


#----- Creating the endpoint routes ------#
@app.route('/home', methods=['GET'])
def home():

    if current_user.is_authenticated:
        return redirect(url_for('account'))
    
    else:
         return render_template('home.html')



@app.route('/member-register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
               
             hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
             user = UserDetails(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data, password=hashed_password)
             db.session.add(user)
             db.session.commit()
             return redirect(url_for('profile'))
        
    


    return render_template('register_quiz.html', form=form)
        



@app.route('/member-profile', methods=['GET', 'POST'])
def profile():

    form = ProfileForm()

    if request.method == 'POST':
        if form.validate_on_submit():
             new_user = UserDetails.query.order_by(UserDetails.id.desc()).first()

             if new_user:
                new_user.date_of_birth = form.date_of_birth.data
                new_user.gender = form.gender.data
                new_user.instagram_link = form.instagram_username.data
                new_user.facebook_link = form.facebook_username.data
                db.session.commit()
                flash('Account information updated successfully', 'success')
                return redirect(url_for('login'))  # Redirect to login page after profile update
            

    return render_template('user_profile.html', form=form) 






@app.route('/member-login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    messages = get_flashed_messages()
    if form.validate_on_submit():
        user = UserDetails.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user) # Get the state of the user that is currently login, so it means that if a user logs in, it is stored in the login_user()
            return redirect(url_for('account'))
        

        else:
            flash('User not found, Please try again')
            return redirect(url_for('login'))
        
    
    return render_template('login_quiz.html', form=form, messages=messages)




@app.route("/account")
@login_required
def account():
    
    present_user = current_user.firstname + ' ' + current_user.lastname
    username = current_user.username
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, present_user=present_user, username=username)




@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def email_validator(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


@app.route("/edit_information", methods=['GET', 'POST'])
@login_required
def edit_information():
    form = UpdateInformation()

    
    if request.method == 'POST':
        if form.validate_on_submit():
             current_user.firstname = form.firstname_update.data
             current_user.lastname = form.lastname_update.data
             current_user.username = form.username_update.data
             current_user.email = form.email_update.data
             current_user.date_of_birth = form.date_of_birth_update.data
             current_user.gender = form.gender_update.data
             current_user.instagram_link = form.ig_username_update.data
             current_user.facebook_link = form.fb_username_update.data
             db.session.commit()
             return redirect(url_for('account'))
        

    elif request.method == 'GET':
             form.firstname_update.data = current_user.firstname
             form.lastname_update.data = current_user.lastname
             form.username_update.data = current_user.username
             form.email_update.data = current_user.email
             form.date_of_birth_update.data = current_user.date_of_birth
             form.gender_update.data = current_user.gender
             form.ig_username_update.data = current_user.instagram_link 
             form.fb_username_update.data = current_user.facebook_link



    return render_template('edit_info.html', form=form)






@app.route('/edit_password', methods=['GET', 'POST'])
def edit_password():

    if request.method == 'POST':
        
        user = UserDetails.query.filter_by(username=current_user.username).first()
        if user and bcrypt.check_password_hash(user.password, request.form['old_password']):
            hashed_new_password = bcrypt.generate_password_hash(request.form['new_password']).decode('utf-8')
            user.password = hashed_new_password
            db.session.commit()
            return redirect(url_for('account'))
        

        else:
            flash('Old password incorrect. Please try again')
            return redirect(url_for('edit_password'))

        


    return render_template("edit_password.html")




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
                user_response = form_data.get(f'Question {question["id"]}.') 
                correct_response = [x for x in question['options'] if x['is_correct']==True] 
                correct_answers.append(correct_response) 
                user_responses[f'Question {question["id"]}'] = user_response
                if user_response == correct_response[0]["letter"]:
                    no_correct_answer += 1

  
            score_percentage = no_correct_answer/total_questions*100
            score_percentage = round(score_percentage, 2)
         
            return make_response(render_template('result1.html', form=form, score_percentage=score_percentage,
                   no_correct_answer=no_correct_answer, total_questions=total_questions, correct_answers=correct_answers))
   
   
       


api.add_resource(Electronics, '/electronics')


@app.route('/electronics/answers')
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