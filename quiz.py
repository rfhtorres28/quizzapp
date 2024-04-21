from flask import Flask, request, render_template, url_for, flash, redirect, get_flashed_messages, make_response, jsonify, session
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt 
from flask_login import current_user, LoginManager, login_user, logout_user, login_required 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import RadioField, HiddenField, StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UnicodeText
from email_validator import validate_email, EmailNotValidError
import secrets
import os 
from datetime import datetime
import random

#-----Initializing the flask app-------#
        
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '582ea1bb8309ccf43fd65b39d593a6a6'
app.secret_key = 'Tootsie@2714'
bcrypt = Bcrypt(app)


#------ configuring the database -------#

username='root'
password= 'Toootsie@1430'
port = '3306'
host = 'localhost'
database_name= 'quizapp'


#-----Initializing the Database-------#


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}?charset=utf8mb4' # Modify MySQL database configuration to include the charset=utf8mb4 parameter to support unicode text
db = SQLAlchemy(app)



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
    gender = db.Column(db.String(10))
    instagram_link = db.Column(db.String(255))
    facebook_link = db.Column(db.String(255))
    bio = db.Column(UnicodeText, nullable=True, default='')

    def __repr__(self):

        return f"User('{self.username}', '{self.email}', '{self.password}')"



class ElecsQuestions(db.Model):

    __tablename__ = 'elecsquestions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('ElecsOptions', backref='elecsquestions', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class ElecsOptions(db.Model):

    __tablename__ = 'elecsoptions'
    id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, db.ForeignKey('elecsquestions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"


class CommsQuestions(db.Model):

    __tablename__ = 'commsquestions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    options = db.relationship('CommsOptions', backref='commsquestions', lazy=True)

    def __repr__(self):

        return f"Question('{self.content}', '{self.options}')"



class CommsOptions(db.Model):

    __tablename__ = 'commsoptions'
    id = db.Column(db.Integer, primary_key=True)
    question_no = db.Column(db.Integer, db.ForeignKey('commsquestions.id'), nullable=False)
    letter = db.Column(db.String(1), nullable=False )
    content = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    def __repr__(self):

        return f"Options('{self.letter}', '{self.content}', '{self.is_correct}')"



class UserResult(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'), nullable=False)
    session_id = db.Column(db.String(50), nullable=False)
    score_percentage = db.Column(db.String(5))
    no_correct_answer = db.Column(db.String(5))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __repr__(self):

        return f"UserSession(session_id='{self.session_id}', timestamp='{self.timestamp}')"


# Creating Electronics Quiz Form

class QuizForm(FlaskForm):
    user_id = HiddenField()



qn = ElecsQuestions.query.all()
opn = ElecsOptions.query.all()
ece_questions = [{"id":question.id, "content":question.content,
                 "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]



# Creating Communications Quiz Form

class CommsQuizForm(FlaskForm):
    user_id = HiddenField()

def create_dynamic_fields(questions):
    
    
    for i, question in enumerate(questions, start=1):
        choices = [(option['letter'], option['content']) for option in question['options']] # a list of tuples, elements can be access same as a list
        field_name = f'Question {i}.'
        field_label = question['content']
        setattr(CommsQuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))



qn = CommsQuestions.query.all()
opn = CommsOptions.query.all()
comms_questions = [{"id":question.id, "content":question.content,
                "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]

create_dynamic_fields(comms_questions)



class RegistrationForm(FlaskForm):
    
    firstname = StringField('Firstname', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Lastname', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Next')
    
    
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
    bio = StringField('Bio')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
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
    bio = StringField('Bio')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
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
            session['registration_data'] = {
                'username': form.username.data,
                'firstname': form.firstname.data,
                'lastname': form.lastname.data,
                'email': form.email.data,
                'password': form.password.data
            }     
            return redirect(url_for('profile'))

    return render_template('register_quiz.html', form=form)
        


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_text = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_text
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn 




@app.route('/member-profile', methods=['GET', 'POST'])
def profile():

    form = ProfileForm()

    if request.method == 'POST':
        if form.validate_on_submit():

             registration_data = session.get('registration_data')
             if registration_data:
                   hashed_password = bcrypt.generate_password_hash(registration_data['password']).decode('utf-8')
                   user = UserDetails(
                          username=registration_data['username'],
                          firstname=registration_data['firstname'],
                          lastname=registration_data['lastname'],
                          email=registration_data['email'],
                          password=hashed_password
                       )
                   db.session.add(user)
                   db.session.flush() # Flush to get the user's ID before committing
                   
                   # Update user profile with profile form data
                   user.date_of_birth = form.date_of_birth.data
                   user.gender = form.gender.data
                   user.instagram_link = form.instagram_username.data
                   user.facebook_link = form.facebook_username.data
                   user.bio = form.bio.data
                   if form.picture.data:
                        picture_file = save_picture(form.picture.data)
                        user.image_file = picture_file
                   db.session.commit()
                   flash('Account registered successfully', 'success')
                   session.pop('registration_data')  # Remove registration data from session
                   return redirect(url_for('login'))
            

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




@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    
    present_user = current_user.firstname + ' ' + current_user.lastname
    username = current_user.username
    bio = current_user.bio
    email = current_user.email
    instagram = f'https://www.instagram.com/{current_user.instagram_link}'
    facebook = f'https://www.facebook.com/{current_user.facebook_link}'
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    record = [] 
    next_page = None
    user = None
    selected_course = ''
 
    
    if request.method == 'POST':
         selected_course = request.form.get('course', '')
         page = request.args.get('page', 1, type=int)
         user = UserResult.query.filter_by(user_id=current_user.id, subject=selected_course).paginate(page=page, per_page=10)
         record = [{"subject":result.subject, "score_percentage":result.score_percentage, "correct_answer": result.no_correct_answer, "timestamp":result.timestamp} for result in user.items]
        

         
    return render_template('account.html', image_file=image_file, present_user=present_user, username=username, bio=bio, record=record, instagram=instagram, facebook=facebook, email=email, user=user, selected_course=selected_course)



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
             current_user.bio = form.bio.data
             
             if form.picture.data:
                        picture_file = save_picture(form.picture.data)
                        current_user.image_file = picture_file
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
             form.picture.data = current_user.image_file
             form.bio.data = current_user.bio



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

field_labels = {}

# Creating API Resource for Electronics Questions 
class Electronics(Resource):
   
   
   @login_required
   def get(self):
       if not current_user.is_authenticated:
            return redirect(url_for('login'))
       
       def create_dynamic_fields(questions):
         
         random.shuffle(questions)
         for i, question in enumerate(questions, start=1):
            choices = [(option['letter'], option['content']) for option in question['options']] # a list of tuples, elements can be access same as a list
            field_name = f'Question {i}'
            field_label = question['content']
            setattr(QuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))
            field_labels[field_name] = field_label
         

       create_dynamic_fields(ece_questions)
       
       form = QuizForm() 
       return make_response(render_template('elecsquiz.html', form=form))
       
   
   def post(self):
            global field_labels
            # Fetching new electronics questions from the administrator     
            if request.data:
                 data = request.json
                 totalquestions = ElecsQuestions.query.count()
                 question = data.get('content')
                 options = data.get('options')

                 if question:
                    question_id = totalquestions + 1
                    new_question = ElecsQuestions(id=question_id, content=question) 
                    db.session.add(new_question)
                    db.session.commit()

                    if options:  
                      id = ElecsOptions.query.count()  
                      question_no = totalquestions + 1     
                      for option_data in options:    
                             id += 1
                             letter = option_data['letter']
                             content = option_data['content']
                             is_correct = option_data['is_correct']
                             new_option = ElecsOptions(id=id, question_no=question_no, letter=letter, content=content, is_correct=is_correct)
                             db.session.add(new_option)
                             db.session.commit()

            

                 return jsonify({"message":"Question added succesfully"})
                 
                               

            form = QuizForm() 
            no_correct_answer = 0
            user_response = []
            total_questions = len(ece_questions)
            correct_options = []
            correct_option = []
            answer_content = []
            questions = []
            session_id = secrets.token_hex(16)
            session['sid'] = session_id

            for question in field_labels.values():
                 questions.append(question)

            # Checking if whether the user response is correct or not, request.form-> user answers, 
            for form_question in field_labels.values():
                for elecs_question in ece_questions:
                    if elecs_question["content"] == form_question:
                        for option in elecs_question["options"]:
                            if option["is_correct"]:
                                    correct_options.append(option)

                   
      

            filtered_form = {key: value for key, value in request.form.items() if key not in ['user_id', 'csrf_token']}

            for value in filtered_form.values():
                user_response.append(value)

            for option in correct_options:
                correct_option.append(option['letter'])
                
            for option in correct_options:
                answer_content.append(option['content'])
            
            for i in range(len(user_response)):
                if user_response[i] == correct_option[i]:
                    no_correct_answer += 1

            session_id = session.get('sid')
            score_percentage = no_correct_answer/total_questions*100
            score_percentage = round(score_percentage, 2)
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_result= {"subject":"Electronics", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time, "correct_answer":answer_content, "question":questions}

            if current_user.is_authenticated:
                session["user_result"] = user_result # store the user_result to the session
                session_user_result = session.get("user_result")

            if session_user_result:
                     score_percentage = session_user_result["score_percentage"]
                     no_correct_answer = session_user_result["no_correct_answer"]
                     timestamp = session_user_result["timestamp"]
                     subject = session_user_result["subject"]
                     
            
            if session_id:
                     new_result = UserResult(user_id=current_user.id, session_id=session_id, subject=subject, score_percentage=score_percentage, no_correct_answer=no_correct_answer, timestamp=timestamp)
                     db.session.add(new_result)
                     db.session.commit()


            return make_response(render_template('elecs_result.html', form=form, score_percentage=score_percentage,
                   no_correct_answer=no_correct_answer, total_questions=total_questions))    
         
   

   
# Creating API Resource for Communications Questions 
class Communications(Resource):
   
   @login_required
   def get(self):
       if not current_user.is_authenticated:
            return redirect(url_for('login'))
       
       form = CommsQuizForm() 
       return make_response(render_template('commsquiz.html', questions=comms_questions, form=form))
       
   
   def post(self):
            
            form = CommsQuizForm() 
            no_correct_answer = 0
            correct_answers = []
            total_questions = len(comms_questions)
            user_responses = {}
            form_data = {}
            user_result = {}
            session_id = secrets.token_hex(16)
            session['sid'] = session_id

           
            if form.validate_on_submit():
                form_data = request.form.to_dict()  
    
            for question in comms_questions: 
                user_response = form_data.get(f'Question {question["id"]}.') 
                correct_response = [x for x in question['options'] if x['is_correct']==True] 
                correct_answers.append(correct_response) 
                user_responses[f'Question {question["id"]}'] = user_response
                if user_response == correct_response[0]["letter"]:
                    no_correct_answer += 1

            session_id = session.get('sid')
            score_percentage = no_correct_answer/total_questions*100
            score_percentage = round(score_percentage, 2)
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_result= {"subject":"Communications", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time}

            if current_user.is_authenticated:
                session["user_result"] = user_result # store the user_result to the session
                session_user_result = session.get("user_result")

            if session_user_result:
                     score_percentage = session_user_result["score_percentage"]
                     no_correct_answer = session_user_result["no_correct_answer"]
                     timestamp = session_user_result["timestamp"]
                     subject = session_user_result["subject"]
                
            if session_id:
                     new_result = UserResult(user_id=current_user.id, session_id=session_id, subject=subject, score_percentage=score_percentage, no_correct_answer=no_correct_answer, timestamp=timestamp)
                     db.session.add(new_result)
                     db.session.commit()


            return make_response(render_template('comms_result.html', form=form, score_percentage=score_percentage,
                   no_correct_answer=no_correct_answer, total_questions=total_questions, correct_answers=correct_answers))  
       


api.add_resource(Electronics, '/electronics')
api.add_resource(Communications, '/communications')





@app.route('/electronics/answers')
@login_required #Safety feature so that user that is not authenticated cant access the correct answers
def elecsanswers():
    answer_key = {}
    correct_answers = session["user_result"]["correct_answer"] 
    questions = session["user_result"]["question"]

    for i in range(len(correct_answers)):
         answer_key[questions[i]] = correct_answers[i] 
   
    return render_template('elecs_answers.html', answer_key=answer_key)



@app.route('/communications/answers')
@login_required #Safety feature so that user that is not authenticated cant access the correct answers
def commsanswers():
    correct_answers = []
    
    if current_user.is_authenticated:
        for question in comms_questions:
            correct_response = [x for x in question['options'] if x['is_correct']==True] 
            correct_answers.append(correct_response)  
             
      

    return render_template('comms_correct_answers.html', correct_answers=correct_answers)




if __name__ == '__main__':
    app.run(debug=True)


# render_template typically returns an html string so use make_response() to ensure 