from flask import Flask, request, render_template, url_for
from ECEbank import ece_questions




app = Flask(__name__)

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')



@app.route('/electronics', methods=['GET', 'POST'])
def elecs():
     
     correct_answer = 0
     correct_letters = []
     total_questions = len(ece_questions)
      

     if request.method == 'GET': 
         return render_template('quiz.html', questions=ece_questions)
     
     elif request.method == 'POST':
        for question in ece_questions: # loop through the list of dictionary questions
            user_response = request.form.get(f'q{question["id"]}') # return the value pair, in this case, the letter choice of the user
            correct_response = [x for x in question['options'] if x['is_correct']==True] # this return the correct answer for each question
            correct_letters.append(correct_response) # or correct_letters.append(correct_response[0] if correct_response else None)
       
            if user_response == correct_response[0]["letter"]:
                correct_answer += 1
        
        score_percentage = correct_answer/total_questions*100
        score_percentage = round(score_percentage, 2)
        return render_template('result.html', correct_letters=correct_letters, 
        correct_answer=correct_answer, total_questions=total_questions, score_percentage=score_percentage)
         
     
        




if __name__ == '__main__':
    app.run(debug=True)