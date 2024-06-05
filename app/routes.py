from flask import Flask, request, render_template, url_for, flash, redirect, get_flashed_messages, session
from .forms import RegistrationForm, ProfileForm, LoginForm, UpdateInformation, QuizForm, CommsQuizForm, ece_questions, comms_questions, math_questions, geas_questions, GEASQuizForm, MathQuizForm
from .models import UserDetails, UserResult
from . import db
from . import app, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import secrets
import random
import os
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import RadioField
from wtforms.validators import InputRequired






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
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
               login_user(user) # Get the state of the user that is currently login, so it means that if a user logs in, it is stored in the login_user()
               return redirect(url_for('account', username=user.username))
            else:
                flash('Password is incorrect, Please try again')
                return redirect(url_for('login'))
        else:
            flash('Email not found, Please try again')
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


# Create an Error Route for 404.html page 
@app.errorhandler(404)
def page_not_found(error):
    if request.path.endswith('.html'):
        return render_template('404.html'), 404
    
    else:
        return "Page Not Found", 404 



# field_labels was put here so that whenever a POST request is made to the electronics route, the field_labels dictionary when retrieving in the POST condition will not be empty
field_labels = {}
@app.route('/electronics', methods=['GET', 'POST'])
@login_required
def electronics():
    
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

      # Creating dynamic form fields for ECE questions 
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
        return render_template('elecsquiz.html', form=form)


    elif request.method == 'POST':
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
                 return render_template('elecs_result.html', form=form, score_percentage=score_percentage,
                        no_correct_answer=no_correct_answer, total_questions=total_questions, messages=messages)
            
            else:
               flash('Complete answering the questions')
               return redirect(url_for('electronics')) 
            


# field_labels was put here so that whenever a POST request is made to the communication route, the field_labels dictionary when retrieving in the POST condition will not be empty
field_labels = {}
@app.route('/communications', methods=['GET', 'POST'])
@login_required
def communications():
    
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

      # Creating dynamic form fields for communications questions 
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
        return render_template('commsquiz.html', form=form)


    elif request.method == 'POST':
            form = CommsQuizForm() 
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
            global session_user_result

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
            user_result= {"subject":"Communications", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time, "correct_answer":answer_content, "question":questions}

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
            


            if form.validate_on_submit(): # when form from the communication quiz route is valid upon submission
                 image_file = url_for('static', filename='../static/profile_pics/' + current_user.image_file)
                 user = UserResult.query.filter_by(session_id=session_user_result["session_id"]).first()
                 if user:
                     user.profile_pic = image_file
                     db.session.commit()
                 return render_template('comms_result.html', form=form, score_percentage=score_percentage,
                        no_correct_answer=no_correct_answer, total_questions=total_questions, messages=messages)
            
            else:
               flash('Complete answering the questions')
               return redirect(url_for('communications')) 
            



# field_labels was put here so that whenever a POST request is made to the math route, the field_labels dictionary when retrieving in the POST condition will not be empty
field_labels = {}
@app.route('/math', methods=['GET', 'POST'])
@login_required
def math():
    
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

      # Creating dynamic form fields for ECE questions 
        def create_dynamic_fields(questions):
         
          random.shuffle(questions)
          for i, question in enumerate(questions, start=1):
              choices = [(option['letter'], option['content']) for option in question['options']] # a list of tuples, elements can be access same as a list
              field_name = f'Question {i}'
              field_label = question['content']
              setattr(MathQuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))
              field_labels[field_name] = field_label
          

        create_dynamic_fields(math_questions)
       
        form = MathQuizForm() 
        return render_template('mathquiz.html', form=form)


    elif request.method == 'POST':
            form = MathQuizForm() 
            no_correct_answer = 0
            user_response = []
            total_questions = len(math_questions)
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
                for math_question in math_questions:
                    if math_question["content"] == form_question:
                        for option in math_question["options"]:
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
            user_result= {"subject":"Math", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time, "correct_answer":answer_content, "question":questions}

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

                 return render_template('math_result.html', form=form, score_percentage=score_percentage,
                        no_correct_answer=no_correct_answer, total_questions=total_questions, messages=messages)
            
            else:
               flash('Complete answering the questions')
               return redirect(url_for('math')) 
            


# field_labels was put here so that whenever a POST request is made to the geas route, the field_labels dictionary when retrieving in the POST condition will not be empty
field_labels = {}
@app.route('/geas', methods=['GET', 'POST'])
@login_required
def geas():
    
    if request.method == 'GET':
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

      # Creating dynamic form fields for GEAS questions 
        def create_dynamic_fields(questions):
         
          random.shuffle(questions)
          for i, question in enumerate(questions, start=1):
              choices = [(option['letter'], option['content']) for option in question['options']] # a list of tuples, elements can be access same as a list
              field_name = f'Question {i}'
              field_label = question['content']
              setattr(GEASQuizForm, field_name, RadioField(field_label, choices=choices, validators=[InputRequired()]))
              field_labels[field_name] = field_label
          

        create_dynamic_fields(geas_questions)
       
        form = GEASQuizForm() 
        return render_template('geasquiz.html', form=form)


    elif request.method == 'POST':
            form = GEASQuizForm() 
            no_correct_answer = 0
            user_response = []
            total_questions = len(geas_questions)
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
                for geas_question in geas_questions:
                    if geas_question["content"] == form_question:
                        for option in geas_question["options"]:
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
            user_result= {"subject":"GEAS", "session_id":session_id, "score_percentage":score_percentage, "no_correct_answer":no_correct_answer, "timestamp":completion_time, "correct_answer":answer_content, "question":questions}

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

                 return render_template('geas_result.html', form=form, score_percentage=score_percentage,
                        no_correct_answer=no_correct_answer, total_questions=total_questions, messages=messages)
            
            else:
               flash('Complete answering the questions')
               return redirect(url_for('geas'))
            

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

        # query user that got top scores in answering electronics quiz
        elecs_user = UserResult.query.filter_by(subject='Electronics').order_by(UserResult.no_correct_answer.desc()).all()
        elecs_scorer = [{"user":user.username, "score":user.score_percentage, "location":user.country} for user in elecs_user]
        scorer_elecs = []


        for item in elecs_scorer:
            if item["user"] not in [x["user"] for x in scorer_elecs]:
                scorer_elecs.append(item)
            else:
                continue

        scorer_elecs = scorer_elecs[:3]    
        
        # query user that got top scores in answering communications quiz
        comms_user = UserResult.query.filter_by(subject='Communications').order_by(UserResult.no_correct_answer.desc()).all()
        comms_scorer = [{"user":user.username, "score":user.score_percentage, "location":user.country} for user in comms_user]
        scorer_comms = []


        for item in comms_scorer:
            if item["user"] not in [x["user"] for x in scorer_comms]:
                scorer_comms.append(item)
            else:
                continue

        scorer_comms = scorer_comms[:3]    


        # query user that got top scores in answering math quiz
        math_user = UserResult.query.filter_by(subject='Math').order_by(UserResult.no_correct_answer.desc()).all()
        math_scorer = [{"user":user.username, "score":user.score_percentage, "location":user.country} for user in math_user]
        scorer_math = []


        for item in math_scorer:
            if item["user"] not in [x["user"] for x in scorer_math]:
                scorer_math.append(item)
            else:
                continue

        scorer_math = scorer_math[:3] 


        # query user that got top scores in answering geas quiz
        geas_user = UserResult.query.filter_by(subject='GEAS').order_by(UserResult.no_correct_answer.desc()).all()
        geas_scorer = [{"user":user.username, "score":user.score_percentage, "location":user.country} for user in geas_user]
        scorer_geas = []


        for item in geas_scorer:
            if item["user"] not in [x["user"] for x in scorer_geas]:
                scorer_geas.append(item)
            else:
                continue

        scorer_geas = scorer_geas[:3]



    return  render_template('quizfeed.html', result_list=result_list, message=message, scorer_elecs=scorer_elecs, scorer_comms=scorer_comms, scorer_math=scorer_math, scorer_geas=scorer_geas)



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



@app.route('/math/answers')
@login_required #Safety feature so that user that is not authenticated cant access the correct answers
def mathanswers():
    answer_key = {}
    correct_answers = session["user_result"]["correct_answer"] 
    questions = session["user_result"]["question"]

    for i in range(len(correct_answers)):
         answer_key[questions[i]] = correct_answers[i] 
   
    return render_template('math_answers.html', answer_key=answer_key)



@app.route('/geas/answers')
@login_required #Safety feature so that user that is not authenticated cant access the correct answers
def geasanswers():
    answer_key = {}
    correct_answers = session["user_result"]["correct_answer"] 
    questions = session["user_result"]["question"]

    for i in range(len(correct_answers)):
         answer_key[questions[i]] = correct_answers[i] 
   
    return render_template('geas_answers.html', answer_key=answer_key)