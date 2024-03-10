from flask import Flask, request, render_template, url_for, flash, jsonify, redirect
from ECEbank import ece_questions
from Questionforms import QuizForm



app = Flask(__name__)
app.config['SECRET_KEY'] = '582ea1bb8309ccf43fd65b39d593a6a6'

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')



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
         
         return render_template('result1.html', form=form, score_percentage=score_percentage,
         no_correct_answer=no_correct_answer, total_questions=total_questions, correct_answers=correct_answers)
            
       
  
     
     return render_template('quiz.html', questions=ece_questions, form=form)
        




if __name__ == '__main__':
    app.run(debug=True)