from flask import Flask, request, render_template, url_for, flash, redirect, get_flashed_messages, make_response, jsonify, session
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt 
from flask_login import current_user, LoginManager, login_user, logout_user, login_required 
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import RadioField, HiddenField, StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UnicodeText
from email_validator import validate_email, EmailNotValidError
import secrets
import os 
from datetime import datetime
import random
from sqlalchemy.ext.hybrid import hybrid_property


#-----Initializing the flask app-------#
        
app = Flask(__name__)
api = Api(app)
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
    country = db.Column(db.String(255))
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


qn = CommsQuestions.query.all()
opn = CommsOptions.query.all()
comms_questions = [{"id":question.id, "content":question.content,
                "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]




class RegistrationForm(FlaskForm):
    
    firstname = StringField('Firstname', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Enter your Firsname"})
    lastname = StringField('Lastname', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Enter your Lastname"})
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Enter your Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Enter your Confirm Password"})
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


countries = [
    ("Afghanistan", "Afghanistan"), ("Albania", "Albania"), ("Algeria", "Algeria"), ("American Samoa", "American Samoa"), ("Andorra", "Andorra"), ("Angola", "Angola"), ("Anguilla", "Anguilla"), ("Antarctica", "Antarctica"), ("Antigua and Barbuda", "Antigua and Barbuda"), ("Argentina", "Argentina"),
    ("Armenia", "Armenia"), ("Aruba", "Aruba"), ("Australia", "Australia"), ("Austria", "Austria"), ("Azerbaijan", "Azerbaijan"), ("Bahamas", "Bahamas"), ("Bahrain", "Bahrain"), ("Bangladesh", "Bangladesh"), ("Barbados", "Barbados"), ("Belarus", "Belarus"),
    ("Belgium", "Belgium"), ("Belize", "Belize"), ("Benin", "Benin"), ("Bermuda", "Bermuda"), ("Bhutan", "Bhutan"), ("Bolivia", "Bolivia"), ("Bosnia and Herzegovina", "Bosnia and Herzegovina"), ("Botswana", "Botswana"), ("Bouvet Island", "Bouvet Island"), ("Brazil", "Brazil"),
    ("British Indian Ocean Territory", "British Indian Ocean Territory"), ("Brunei Darussalam", "Brunei Darussalam"), ("Bulgaria", "Bulgaria"), ("Burkina Faso", "Burkina Faso"), ("Burundi", "Burundi"), ("Cambodia", "Cambodia"), ("Cameroon", "Cameroon"), ("Canada", "Canada"), ("Cape Verde", "Cape Verde"), ("Cayman Islands", "Cayman Islands"),
    ("Central African Republic", "Central African Republic"), ("Chad", "Chad"), ("Chile", "Chile"), ("China", "China"), ("Christmas Island", "Christmas Island"), ("Cocos (Keeling) Islands", "Cocos (Keeling) Islands"), ("Colombia", "Colombia"), ("Comoros", "Comoros"), ("Congo", "Congo"), ("Congo, the Democratic Republic of the", "Congo, the Democratic Republic of the"),
    ("Cook Islands", "Cook Islands"), ("Costa Rica", "Costa Rica"), ("Cote D'Ivoire", "Cote D'Ivoire"), ("Croatia", "Croatia"), ("Cuba", "Cuba"), ("Cyprus", "Cyprus"), ("Czech Republic", "Czech Republic"), ("Denmark", "Denmark"), ("Djibouti", "Djibouti"), ("Dominica", "Dominica"),
    ("Dominican Republic", "Dominican Republic"), ("Ecuador", "Ecuador"), ("Egypt", "Egypt"), ("El Salvador", "El Salvador"), ("Equatorial Guinea", "Equatorial Guinea"), ("Eritrea", "Eritrea"), ("Estonia", "Estonia"), ("Ethiopia", "Ethiopia"), ("Falkland Islands (Malvinas)", "Falkland Islands (Malvinas)"), ("Faroe Islands", "Faroe Islands"),
    ("Fiji", "Fiji"), ("Finland", "Finland"), ("France", "France"), ("French Guiana", "French Guiana"), ("French Polynesia", "French Polynesia"), ("French Southern Territories", "French Southern Territories"), ("Gabon", "Gabon"), ("Gambia", "Gambia"), ("Georgia", "Georgia"), ("Germany", "Germany"),
    ("Ghana", "Ghana"), ("Gibraltar", "Gibraltar"), ("Greece", "Greece"), ("Greenland", "Greenland"), ("Grenada", "Grenada"), ("Guadeloupe", "Guadeloupe"), ("Guam", "Guam"), ("Guatemala", "Guatemala"), ("Guinea", "Guinea"), ("Guinea-Bissau", "Guinea-Bissau"),
    ("Guyana", "Guyana"), ("Haiti", "Haiti"), ("Heard Island and Mcdonald Islands", "Heard Island and Mcdonald Islands"), ("Holy See (Vatican City State)", "Holy See (Vatican City State)"), ("Honduras", "Honduras"), ("Hong Kong", "Hong Kong"), ("Hungary", "Hungary"), ("Iceland", "Iceland"), ("India", "India"),
    ("Indonesia", "Indonesia"), ("Iran, Islamic Republic of", "Iran, Islamic Republic of"), ("Iraq", "Iraq"), ("Ireland", "Ireland"), ("Israel", "Israel"), ("Italy", "Italy"), ("Jamaica", "Jamaica"), ("Japan", "Japan"), ("Jordan", "Jordan"), ("Kazakhstan", "Kazakhstan"),
    ("Kenya", "Kenya"), ("Kiribati", "Kiribati"), ("Korea, Democratic People's Republic of", "Korea, Democratic People's Republic of"), ("Korea, Republic of", "Korea, Republic of"), ("Kuwait", "Kuwait"), ("Kyrgyzstan", "Kyrgyzstan"), ("Lao People's Democratic Republic", "Lao People's Democratic Republic"), ("Latvia", "Latvia"), ("Lebanon", "Lebanon"),
    ("Lesotho", "Lesotho"), ("Liberia", "Liberia"), ("Libyan Arab Jamahiriya", "Libyan Arab Jamahiriya"), ("Liechtenstein", "Liechtenstein"), ("Lithuania", "Lithuania"), ("Luxembourg", "Luxembourg"), ("Macao", "Macao"), ("Macedonia, the Former Yugoslav Republic of", "Macedonia, the Former Yugoslav Republic of"), ("Madagascar", "Madagascar"),
    ("Malawi", "Malawi"), ("Malaysia", "Malaysia"), ("Maldives", "Maldives"), ("Mali", "Mali"), ("Malta", "Malta"), ("Marshall Islands", "Marshall Islands"), ("Martinique", "Martinique"), ("Mauritania", "Mauritania"), ("Mauritius", "Mauritius"), ("Mayotte", "Mayotte"),
    ("Mexico", "Mexico"), ("Micronesia, Federated States of", "Micronesia, Federated States of"), ("Moldova, Republic of", "Moldova, Republic of"), ("Monaco", "Monaco"), ("Mongolia", "Mongolia"), ("Montserrat", "Montserrat"), ("Morocco", "Morocco"), ("Mozambique", "Mozambique"), ("Myanmar", "Myanmar"),
    ("Namibia", "Namibia"), ("Nauru", "Nauru"), ("Nepal", "Nepal"), ("Netherlands", "Netherlands"), ("Netherlands Antilles", "Netherlands Antilles"), ("New Caledonia", "New Caledonia"), ("New Zealand", "New Zealand"), ("Nicaragua", "Nicaragua"), ("Niger", "Niger"), ("Nigeria", "Nigeria"),
    ("Niue", "Niue"), ("Norfolk Island", "Norfolk Island"), ("Northern Mariana Islands", "Northern Mariana Islands"), ("Norway", "Norway"), ("Oman", "Oman"), ("Pakistan", "Pakistan"), ("Palau", "Palau"), ("Palestinian Territory, Occupied", "Palestinian Territory, Occupied"), ("Panama", "Panama"), ("Papua New Guinea", "Papua New Guinea"),
    ("Paraguay", "Paraguay"), ("Peru", "Peru"), ("Philippines", "Philippines"), ("Pitcairn", "Pitcairn"), ("Poland", "Poland"), ("Portugal", "Portugal"), ("Puerto Rico", "Puerto Rico"), ("Qatar", "Qatar"), ("Reunion", "Reunion"), ("Romania", "Romania"), ("Russian Federation", "Russian Federation"),
    ("Rwanda", "Rwanda"), ("Saint Helena", "Saint Helena"), ("Saint Kitts and Nevis", "Saint Kitts and Nevis"), ("Saint Lucia", "Saint Lucia"), ("Saint Pierre and Miquelon", "Saint Pierre and Miquelon"), ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"), ("Samoa", "Samoa"), ("San Marino", "San Marino"), ("Sao Tome and Principe", "Sao Tome and Principe"),
    ("Saudi Arabia", "Saudi Arabia"), ("Senegal", "Senegal"), ("Serbia and Montenegro", "Serbia and Montenegro"), ("Seychelles", "Seychelles"), ("Sierra Leone", "Sierra Leone"), ("Singapore", "Singapore"), ("Slovakia", "Slovakia"), ("Slovenia", "Slovenia"), ("Solomon Islands", "Solomon Islands"), ("Somalia", "Somalia"),
    ("South Africa", "South Africa"), ("South Georgia and the South Sandwich Islands", "South Georgia and the South Sandwich Islands"), ("Spain", "Spain"), ("Sri Lanka", "Sri Lanka"), ("Sudan", "Sudan"), ("Suriname", "Suriname"), ("Svalbard and Jan Mayen", "Svalbard and Jan Mayen"), ("Swaziland", "Swaziland"), ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"), ("Syrian Arab Republic", "Syrian Arab Republic"), ("Taiwan, Province of China", "Taiwan, Province of China"), ("Tajikistan", "Tajikistan"), ("Tanzania, United Republic of", "Tanzania, United Republic of"), ("Thailand", "Thailand"), ("Timor-Leste", "Timor-Leste"), ("Togo", "Togo"), ("Tokelau", "Tokelau"),
    ("Tonga", "Tonga"), ("Trinidad and Tobago", "Trinidad and Tobago"), ("Tunisia", "Tunisia"), ("Turkey", "Turkey"), ("Turkmenistan", "Turkmenistan"), ("Turks and Caicos Islands", "Turks and Caicos Islands"), ("Tuvalu", "Tuvalu"), ("Uganda", "Uganda"), ("Ukraine", "Ukraine"), ("United Arab Emirates", "United Arab Emirates"),
    ("United Kingdom", "United Kingdom"), ("United States", "United States"), ("United States Minor Outlying Islands", "United States Minor Outlying Islands"), ("Uruguay", "Uruguay"), ("Uzbekistan", "Uzbekistan"), ("Vanuatu", "Vanuatu"), ("Venezuela", "Venezuela"), ("Viet Nam", "Viet Nam"), ("Virgin Islands, British", "Virgin Islands, British"),
    ("Virgin Islands, U.s.", "Virgin Islands, U.s."), ("Wallis and Futuna", "Wallis and Futuna"), ("Western Sahara", "Western Sahara"), ("Yemen", "Yemen"), ("Zambia", "Zambia"), ("Zimbabwe", "Zimbabwe")]




class ProfileForm(FlaskForm):

    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    instagram_username = StringField('Instagram', validators=[DataRequired()], render_kw={"placeholder": "Enter your Instagram Username"})
    facebook_username = StringField('Facebook', validators=[DataRequired()], render_kw={"placeholder": "Enter your Facebook Username"})
    date_of_birth = DateField('Date of Birth')
    bio = StringField('Bio', render_kw={"placeholder": "Enter your Bio"})
    country = SelectField('Country', choices=countries)
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
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
        return redirect(url_for('account', username=current_user.username))
    
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
        

# function for saving picture
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
                   user.country = form.country.data
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
            return redirect(url_for('account', username=user.username))
        else:
            flash('User not found, Please try again')
            return redirect(url_for('login'))
        
    
    return render_template('login_quiz.html', form=form, messages=messages)



@app.route("/account/<username>", methods=['GET', 'POST'])
@login_required
def account(username):

    user = UserDetails.query.filter_by(username=username).first()
    if user:
      present_user = user.firstname + ' ' + user.lastname
      username = user.username
      bio = user.bio
      email = user.email
      instagram = f'https://www.instagram.com/{user.instagram_link}'
      facebook = f'https://www.facebook.com/{user.facebook_link}'
      image_file = url_for('static', filename='../static/profile_pics/' + current_user.image_file)   
      profile_pic = url_for('static', filename='../static/profile_pics/' + user.image_file)
      location = user.country
      record = []    
      selected_course = ''
      

      if request.method == 'POST':
        selected_course = request.form.get('course', '')
        session['selected_course'] = selected_course  # Store selected course in session
      else:
           selected_course = session.get('selected_course', '')  # Retrieve selected course from session

      page = request.args.get('page', 1, type=int)
      user_course = UserResult.query.filter_by(user_id=user.id, subject=selected_course).paginate(page=page, per_page=10)
      record = [{"subject": result.subject, "score_percentage": result.score_percentage, "correct_answer": result.no_correct_answer, "timestamp": result.posted_time} for result in user_course.items]

         
      return render_template('account.html', location=location, profile_pic=profile_pic, image_file=image_file, present_user=present_user, username=username, bio=bio, record=record, instagram=instagram, facebook=facebook, email=email, user_course=user_course, selected_course=selected_course, user=user)
    
    else:
        return 'User not found', 404


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

             #Update username on UserDetails table
             user = UserResult.query.filter_by(user_id=current_user.id).all()
             for user in user:
                 user.username = current_user.username
                 db.session.commit()
             
             # Update profile picture on UserResult table
             image_file = url_for('static', filename='../static/profile_pics/' + current_user.image_file)
             user = UserResult.query.filter_by(username=current_user.username).all()
             for user in user:
                 user.profile_pic = image_file
                 db.session.commit()
             


             return redirect(url_for('account', username=current_user.username))
        

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
            return redirect(url_for('account', username=current_user.username))
        

        else:
            flash('Old password incorrect. Please try again')
            return redirect(url_for('edit_password'))

        


    return render_template("edit_password.html")


@app.route('/delete-account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        user_choice = request.form.get('delete_account')
        user_account= UserDetails.query.filter_by(username=current_user.username).first() # returns the row that has the username=current_user.username
        user_result = UserResult.query.filter_by(username=current_user.username).all() # return all rows in the database that has username=current_user.username
        if user_choice: 
           #loops and delete every row in the user_result
           for row in user_result:
                db.session.delete(row)
                db.session.commit()
           db.session.delete(user_account)
           db.session.commit()
           flash('Account deleted succesfully')
           return redirect(url_for('login'))

    return render_template('delete_account.html')


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
            messages = get_flashed_messages()
            global session_user_result

            for question in field_labels.values():
                 questions.append(question)

            # Checking if whether the user response is correct or not, request.form-> user answers, 
            for form_question in field_labels.values():
                for elecs_question in ece_questions:
                    if elecs_question["content"] == form_question:
                        for option in elecs_question["options"]:
                            if option["is_correct"]:
                                    correct_options.append(option)

            if correct_options:  # Check if correct_options is not empty before proceeding
               for option in correct_options:
                  correct_option.append(option['letter'])
                  answer_content.append(option['content'])   
      

            filtered_form = {key: value for key, value in request.form.items() if key not in ['user_id', 'csrf_token']}

            for value in filtered_form.values():
                user_response.append(value)

           
            
            for i in range(len(user_response)):
                if user_response[i] == correct_option[i]:
                    no_correct_answer += 1

            session_id = session.get('sid')
            score_percentage = no_correct_answer/total_questions*100
            score_percentage = round(score_percentage, 2)
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_result= {"subject":"Electronics", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time, "correct_answer":answer_content, "question":questions}

            if current_user.is_authenticated:
                username = current_user.username 
                country = current_user.country
                session["user_result"] = user_result # store the user_result to the session
                session_user_result = session.get("user_result")


            if session_user_result:
                     score_percentage = session_user_result["score_percentage"]
                     no_correct_answer = session_user_result["no_correct_answer"]
                     timestamp = session_user_result["timestamp"] 
                     subject = session_user_result["subject"]
                     
            
            if session_id:
                     new_result = UserResult(user_id=current_user.id, username=username, country=country, session_id=session_id, subject=subject, score_percentage=score_percentage, no_correct_answer=no_correct_answer, posted_time=timestamp)
                     db.session.add(new_result)
                     db.session.commit()
            
           
            if form.validate_on_submit(): # when form from the electronics quiz route is valid upon submission
                 image_file = url_for('static', filename='../static/profile_pics/' + current_user.image_file)
                 user = UserResult.query.filter_by(session_id=session_user_result["session_id"]).first()
                 if user:
                     user.profile_pic = image_file
                     db.session.commit()
                 return make_response(render_template('elecs_result.html', form=form, score_percentage=score_percentage,
                        no_correct_answer=no_correct_answer, total_questions=total_questions, messages=messages))
            
            else:
               flash('Complete answering the questions')
               return redirect(url_for('electronics')) 
            


@app.route("/quizfeed/<username>", methods=["GET"])
@login_required
def quizfeed(username):
    
    
    result_list = []
    user = UserResult.query.order_by(UserResult.posted_time.desc()).all()
    if user is None: 
        message = "No user result found"

    else: 
        result_list = [{"username":result.username, "subject":result.subject, "score_pct":result.score_percentage, "timestamp":result.posted_time, "difference":result.difference, "user_pic":result.profile_pic} for result in user]
        message = None
        print(result_list)
        # Updated the latest_login column everytime quizfeed route is refresh
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        for row in user:
            print(row)
            row.latest_login = current_time
            db.session.commit()
        
        # Give the length of time from it was posted until the current time
        for row in user: 
            delta = row.time_difference
            if delta.total_seconds() > 86400:
                total_days = delta.total_seconds() // 86400
                row.difference = f'{int(total_days)}d ago'
                db.session.commit()

            elif delta.total_seconds() > 3600:
                total_hours = delta.total_seconds() // 3600
                row.difference = f'{int(total_hours)}h ago'
                db.session.commit()

            elif delta.total_seconds() > 60:
                total_min = delta.total_seconds() // 60
                row.difference = f'{int(total_min)}min ago'
                db.session.commit()
            
            else:
                total_sec = delta.total_seconds()
                row.difference = f'{int(total_sec)}s ago'
                db.session.commit()
        
        # delete user result post on quizfeed if the time difference is more than or equal to 1d ago
        user_result = UserResult.query.all()
        for user in user_result:
            if user:
                delta = user.time_difference.total_seconds()
                if delta > 86400:
                    db.session.delete(user)
                    db.session.commit()


        elecs_user = UserResult.query.filter_by(subject='Electronics').order_by(UserResult.no_correct_answer.desc()).all()
        elecs_scorer = [{"user":user.username, "score":user.score_percentage, "location":user.country} for user in elecs_user]
        scorer_elecs = []


        for item in elecs_scorer:
            if item["user"] not in [x["user"] for x in scorer_elecs]:
                scorer_elecs.append(item)
            else:
                continue

        scorer_elecs = scorer_elecs[:3]    
        

        comms_user = UserResult.query.filter_by(subject='Communication').order_by(UserResult.no_correct_answer.desc()).all()
        comms_scorer = [{"user":user.username, "score":user.score_percentage, "location":user.country} for user in comms_user]
        scorer_comms = []


        for item in comms_scorer:
            if item["user"] not in [x["user"] for x in scorer_comms]:
                scorer_comms.append(item)
            else:
                continue

        scorer_comms = scorer_comms[:3]    
        

    return render_template('quizfeed.html', result_list=result_list, message=message, scorer_elecs=scorer_elecs, scorer_comms=scorer_comms)


   
# Creating API Resource for Communications Questions 
class Communications(Resource):
   
   
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
            setattr(CommsQuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))
            field_labels[field_name] = field_label
         

       create_dynamic_fields(comms_questions)
       
       form = CommsQuizForm() 
       return make_response(render_template('commsquiz.html', form=form))
       
   
   def post(self):
            global field_labels
            # Fetching new electronics questions from the administrator     
            if request.data:
                 data = request.json
                 totalquestions = CommsQuestions.query.count()
                 question = data.get('content')
                 options = data.get('options')

                 if question:
                    question_id = totalquestions + 1
                    new_question = CommsQuestions(id=question_id, content=question) 
                    db.session.add(new_question)
                    db.session.commit()

                    if options:  
                      id = CommsOptions.query.count()  
                      question_no = totalquestions + 1     
                      for option_data in options:    
                             id += 1
                             letter = option_data['letter']
                             content = option_data['content']
                             is_correct = option_data['is_correct']
                             new_option = CommsOptions(id=id, question_no=question_no, letter=letter, content=content, is_correct=is_correct)
                             db.session.add(new_option)
                             db.session.commit()

            

                 return jsonify({"message":"Question added succesfully"})
                              

            form = QuizForm() 
            no_correct_answer = 0
            user_response = []
            total_questions = len(comms_questions)
            correct_options = []
            correct_option = []
            answer_content = []
            questions = []
            session_id = secrets.token_hex(16)
            session['sid'] = session_id
            messages = get_flashed_messages()

            for question in field_labels.values():
                 questions.append(question)

            # Checking if whether the user response is correct or not, request.form-> user answers, 
            for form_question in field_labels.values():
                for comms_question in comms_questions:
                    if comms_question["content"] == form_question:
                        for option in comms_question["options"]:
                            if option["is_correct"]:
                                    correct_options.append(option)

            if correct_options:  # Check if correct_options is not empty before proceeding
               for option in correct_options:
                  correct_option.append(option['letter'])
                  answer_content.append(option['content'])   
      

            filtered_form = {key: value for key, value in request.form.items() if key not in ['user_id', 'csrf_token']}

            for value in filtered_form.values():
                user_response.append(value)

            
            for i in range(len(user_response)):
                if user_response[i] == correct_option[i]:
                    no_correct_answer += 1

            session_id = session.get('sid')
            score_percentage = no_correct_answer/total_questions*100
            score_percentage = round(score_percentage, 2)
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_result= {"subject":"Communication", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time, "correct_answer":answer_content, "question":questions}

            if current_user.is_authenticated:
                username = current_user.username 
                country = current_user.country
                session["user_result"] = user_result # store the user_result to the session
                session_user_result = session.get("user_result")

            if session_user_result:
                     score_percentage = session_user_result["score_percentage"]
                     no_correct_answer = session_user_result["no_correct_answer"]
                     timestamp = session_user_result["timestamp"]
                     subject = session_user_result["subject"]
                     
            
            if session_id:
                     new_result = UserResult(user_id=current_user.id, username=username, country=country, session_id=session_id, subject=subject, score_percentage=score_percentage, no_correct_answer=no_correct_answer, posted_time=timestamp)
                     db.session.add(new_result)
                     db.session.commit()
            
           
            if form.validate_on_submit(): # this also returns a POST request 
                 image_file = url_for('static', filename='../static/profile_pics/' + current_user.image_file)
                 user = UserResult.query.filter_by(session_id=session_user_result["session_id"]).first()
                 if user:
                     user.profile_pic = image_file
                     db.session.commit()
                 return make_response(render_template('comms_result.html', form=form, score_percentage=score_percentage,
                        no_correct_answer=no_correct_answer, total_questions=total_questions, messages=messages))
            
            else:
               flash('Complete answering the questions')
               return redirect(url_for('communication')) 
       


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
    answer_key = {}
    correct_answers = session["user_result"]["correct_answer"] 
    questions = session["user_result"]["question"]

    for i in range(len(correct_answers)):
         answer_key[questions[i]] = correct_answers[i] 
   
    return render_template('comms_answers.html', answer_key=answer_key)




if __name__ == "__main__": 
    app.run(host='localhost', debug=True)


# render_template typically returns an html string so use make_response() to ensure 