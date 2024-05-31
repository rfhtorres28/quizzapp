from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
from wtforms import HiddenField
from .models import UserDetails, ElecsQuestions, ElecsOptions, CommsQuestions, CommsOptions, MathQuestions, MathOptions, GEASQuestions, GEASOptions



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


# Creating Math Quiz Form

class MathQuizForm(FlaskForm):
    user_id = HiddenField()


qn = MathQuestions.query.all()
opn = MathOptions.query.all()
math_questions = [{"id":question.id, "content":question.content,
                "options":[{"question_no":question.id, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]


# Creating GEAS Quiz Form

class GEASQuizForm(FlaskForm):
    user_id = HiddenField()


qn = GEASQuestions.query.all()
opn = GEASOptions.query.all()
geas_questions = [{"id":question.id, "content":question.content,
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
    date_of_birth_update = DateField('Birthdate')
    bio = StringField('Bio')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username(self, username_update):

        user = UserDetails.query.filter_by(username=username_update.data).first()

        if user:
            raise ValidationError('Username is already taken')
        