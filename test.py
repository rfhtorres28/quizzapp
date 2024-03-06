from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

questions = [{'id': 1, 'content': 'What is the meaning of B in BJT transistor?',
            'options': [ {'id': 'a', 'content': 'Bipolar', 'is_correct':True},
            {'id': 'b', 'content': 'Bisexual', 'is_correct':False},
            {'id': 'c', 'content': 'Bi-Current', 'is_correct':False} ]

},

{
    'id': 2, 
    'content': 'What is the meaning of J in BJT transistor?',
    'options': [
            {'id': 'a', 'content': 'Junction', 'is_correct':True},
            {'id': 'b', 'content': 'Jeje', 'is_correct':False},
            {'id': 'c', 'content': 'Jayson', 'is_correct':False}

    ]

},


]

@app.route('/')
def index():
    return render_template('quiz.html', questions=questions)


@app.route('/submit', methods=['POST'])
def submit_form():

    correct_answer = 0
 
    for question in questions: # loop through the list of dictionary questions
        user_response = request.form.get(f'q{question["id"]}') # return the value pair, in this case, the letter choice of the user
        correct_response = [x for x in question['options'] if x['is_correct']==True] # this return the correct answer for each question
        

        if user_response == correct_response[0]["id"]:
                correct_answer += 1

    return jsonify(f'You got {correct_answer} out of {len(questions)}, {correct_answer/len(questions)*100}%')



    
     

    
    
    



if __name__ == '__main__':
    app.run(debug=True)