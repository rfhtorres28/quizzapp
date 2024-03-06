from flask import Flask, render_template, request, jsonify, make_response
from flask_restful import Api, Resource
from questionbank import questions




app = Flask(__name__)
api = Api(app)



class SpecificQuestion(Resource):
    def get(self, question_id=None):    
        if question_id is None:
            return questions 
        response = {'message': 'No question found'}
        return jsonify(questions[question_id-1]) if question_id >=1 and question_id <= len(questions) else make_response(jsonify(response), 404)



class Results(Resource):
    def post(self):
        correct_answer = 0
        lis = {}
        for question in questions: # loop through the list of dictionary questions
             user_response = request.form.get(f'q{question["id"]}') # return the value pair, in this case, the letter choice of the user
             correct_response = [x for x in question['options'] if x['is_correct']==True] # this return the correct answer for each question

             if user_response == correct_response[0]["letter"]:
                  correct_answer += 1

        return jsonify(correct_answer)


api.add_resource(SpecificQuestion, '/questions', '/questions/<int:question_id>')
api.add_resource(Results, '/submit')



@app.route('/')
def quiz():
    return render_template('quiz.html', questions=questions)




if __name__ == '__main__':
    app.run(debug=True)