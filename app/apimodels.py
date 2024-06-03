from flask import request, jsonify
from flask_restful import Resource
from .models import ElecsQuestions, ElecsOptions, CommsQuestions, CommsOptions, MathQuestions, MathOptions, GEASOptions, GEASQuestions
from . import db, api
from sqlalchemy import func




# Creating API Class for to manage Electronics Questions 
class ElectronicsQuestionsAPI(Resource):
   

   # # Retrieve questions from the database
   def get(self):     
           questions = ElecsQuestions.query.all()
           elecs_questions = [{"question_id":question.id, "question":question.content} for question in questions]
           data = {"elecs_questions":elecs_questions}
           print(data)
           return jsonify(data)
           

   # Fetching new electronics questions from the administrator 
   def post(self):
            print('post request ')
            global field_labels
                
            if request.data:
                 data = request.json
                 max_question_id = db.session.query(func.max(ElecsQuestions.id)).scalar()
                 max_option_id = db.session.query(func.max(ElecsOptions.id)).scalar()
                 question = data.get('content')
                 options = data.get('options')

                 # Set the value of max_question_id and max_option_id to 0 if their value is None (No questions is in the database)
                 if max_question_id is None:
                        max_question_id = 0

                 if max_option_id is None:
                     max_option_id = 0

                 if question:
                    new_question_id = max_question_id + 1
                    new_question = ElecsQuestions(id=new_question_id, content=question) 
                    db.session.add(new_question)
                    db.session.flush() 

                    if options:     
                      for option_data in options:    
                             max_option_id += 1
                             letter = option_data['letter']
                             content = option_data['content']
                             is_correct = option_data['is_correct']
                             new_option = ElecsOptions(id=max_option_id, question_no=new_question_id, letter=letter, content=content, is_correct=is_correct)
                             db.session.add(new_option)
                             

                 db.session.commit()
                 return jsonify({"message":"Question added succesfully"})
   
   # Update questions from the database        
   def put(self):
       print("PUT request is received")
       data = request.get_json()
       update_question_id = data.get('question_id')
       new_question = data.get('q_content')
       
       update_question = ElecsQuestions.query.filter_by(id=update_question_id).first()

       if update_question: 
           update_question.content = new_question   
       
       db.session.commit()

       return jsonify({"update_question_id":update_question_id, "new_question":new_question})
    

   # delete questions from the database
   def delete(self):
       delete_question_id = request.form.get('question_id')
       question = ElecsQuestions.query.filter_by(id=delete_question_id).first()
     
       if delete_question_id:
           db.session.delete(question)
       
       db.session.commit()
           
       print({'message': 'Question deleted successfully'}, 200)

   


# Create an API Endpoint for Electronics Questions
api.add_resource(ElectronicsQuestionsAPI, '/elecsqn-api')                               


# Creating API Class for to manage Electronics Options 
class ElectronicsChoicesAPI(Resource):

    def get(self):
        qn = ElecsQuestions.query.all()
        opn = ElecsOptions.query.all()
        elecs_questions = [{"id":question.id, "content":question.content, "options":[{"question_no":option.question_no, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]
        return jsonify(elecs_questions)
    
    def put(self):
        data = request.get_json()
        options = data.get('options')
        print(data)
        questions = ElecsOptions.query.filter_by(question_no=data.get('question_id')).all()
        for question in questions:
            for option in options:
               if question.letter == option.get('letter'):
                   question.content = option.get('content')
                   question.is_correct = option.get('is_correct')
                   db.session.flush()
                   
        
        db.session.commit()

        return jsonify(data)


# Create an API Endpoint for Choices of Electronics Choices
api.add_resource(ElectronicsChoicesAPI, '/elecsopn-api')


# Creating API Class for to manage Communication Questions 
class CommunicationQuestionsAPI(Resource):
   
   # Retrieve questions from the database
   def get(self):
           questions = CommsQuestions.query.all()
           comms_questions = [{"question_id":question.id, "question":question.content} for question in questions]
           data = {"comms_questions":comms_questions}
           print('Question retrieve from the database successfully')
           return jsonify(data)
           

   # Fetching new communication questions from the administrator 
   def post(self):
            global field_labels
                
            if request.data:
                 data = request.json
                 max_question_id = db.session.query(func.max(CommsQuestions.id)).scalar()
                 max_option_id = db.session.query(func.max(CommsOptions.id)).scalar()
                 question = data.get('content')
                 options = data.get('options')

                 # Set the value of max_question_id and max_option_id to 0 if their value is None (No questions is in the database)
                 if max_question_id is None:
                        max_question_id = 0

                 if max_option_id is None:
                     max_option_id = 0

                 if question:
                    
                    new_question_id = max_question_id + 1
                    new_question = CommsQuestions(id=new_question_id, content=question) 
                    db.session.add(new_question)
                    db.session.flush() 

                    if options:     
                      for option_data in options:    
                             max_option_id += 1
                             letter = option_data['letter']
                             content = option_data['content']
                             is_correct = option_data['is_correct']
                             new_option = CommsOptions(id=max_option_id, question_no=new_question_id, letter=letter, content=content, is_correct=is_correct)
                             db.session.add(new_option)
                             

                 db.session.commit()
                 return jsonify({"message":"Question added succesfully"})


   # Update questions from the database        
   def put(self):
       print("PUT request is received")
       data = request.get_json()
       update_question_id = data.get('question_id')
       new_question = data.get('q_content')
       
       update_question = CommsQuestions.query.filter_by(id=update_question_id).first()

       if update_question: 
           update_question.content = new_question   
       
       db.session.commit()

       return jsonify({"update_question_id":update_question_id, "new_question":new_question})
    

   # delete questions from the database
   def delete(self):
       delete_question_id = request.form.get('question_id')
       question = CommsQuestions.query.filter_by(id=delete_question_id).first()
     
       if delete_question_id:
           db.session.delete(question)
       
       db.session.commit()
           
       print({'message': 'Question deleted successfully'}, 200)
            


# Create an API Endpoint for Communication Resource
api.add_resource(CommunicationQuestionsAPI, '/commsqn-api')

# Creating API Class for to manage Communication Options 
class CommunicationsChoicesAPI(Resource):

    def get(self):
        qn = CommsQuestions.query.all()
        opn = CommsOptions.query.all()
        elecs_questions = [{"id":question.id, "content":question.content, "options":[{"question_no":option.question_no, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]
        return jsonify(elecs_questions)
   
    def put(self):
        data = request.get_json()
        options = data.get('options')
        print(data)
        questions = CommsOptions.query.filter_by(question_no=data.get('question_id')).all()
        for question in questions:
            for option in options:
               if question.letter == option.get('letter'):
                   question.content = option.get('content')
                   question.is_correct = option.get('is_correct')
                   db.session.flush()
                   
        
        db.session.commit()

        return jsonify(data)


# Create an API Endpoint for Choices of Communication Questions
api.add_resource(CommunicationsChoicesAPI, '/commsopn-api') 



# Creating API Class for to manage Math Questions 
class MathQuestionsAPI(Resource):
   
   # Retrieve questions from the database
   def get(self):
           questions = MathQuestions.query.all()
           math_questions = [{"question_id":question.id, "question":question.content} for question in questions]
           data = {"math_questions":math_questions}
           print('Question retrieve from the database successfully')
           return jsonify(data)
           

   # Fetching new math questions from the administrator 
   def post(self):
            print('hehe')
            global field_labels
                
            if request.data:
                 data = request.json
                 max_question_id = db.session.query(func.max(MathQuestions.id)).scalar()
                 max_option_id = db.session.query(func.max(MathOptions.id)).scalar()
                 question = data.get('content')
                 options = data.get('options')

                 # Set the value of max_question_id and max_option_id to 0 if their value is None (No questions is in the database)
                 if max_question_id is None:
                        max_question_id = 0

                 if max_option_id is None:
                     max_option_id = 0

                 if question:
                    
                    new_question_id = max_question_id + 1
                    new_question = MathQuestions(id=new_question_id, content=question) 
                    db.session.add(new_question)
                    db.session.flush() 

                    if options:     
                      for option_data in options:    
                             max_option_id += 1
                             letter = option_data['letter']
                             content = option_data['content']
                             is_correct = option_data['is_correct']
                             new_option = MathOptions(id=max_option_id, question_no=new_question_id, letter=letter, content=content, is_correct=is_correct)
                             db.session.add(new_option)
                             

                 db.session.commit()
                 return jsonify({"message":"Question added succesfully"})


   # Update questions from the database        
   def put(self):
       print("PUT request is received")
       data = request.get_json()
       update_question_id = data.get('question_id')
       new_question = data.get('q_content')
       
       update_question = MathQuestions.query.filter_by(id=update_question_id).first()

       if update_question: 
           update_question.content = new_question   
       
       db.session.commit()

       return jsonify({"update_question_id":update_question_id, "new_question":new_question})
    

   # delete questions from the database
   def delete(self):
       delete_question_id = request.form.get('question_id')
       question = MathQuestions.query.filter_by(id=delete_question_id).first()
     
       if delete_question_id:
           db.session.delete(question)
       
       db.session.commit()
           
       print({'message': 'Question deleted successfully'}, 200)
            

# Create an API Endpoint for Math Resource
api.add_resource(MathQuestionsAPI, '/mathqn-api')


# Creating API Class to manage Math Choices 
class MathChoicesAPI(Resource):

    def get(self):
        qn = MathQuestions.query.all()
        opn = MathOptions.query.all()
        math_questions = [{"id":question.id, "content":question.content, "options":[{"question_no":option.question_no, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]
        return jsonify(math_questions)
   

    def put(self):
        data = request.get_json()
        options = data.get('options')
        print(data)
        questions = MathOptions.query.filter_by(question_no=data.get('question_id')).all()
        for question in questions:
            for option in options:
               if question.letter == option.get('letter'):
                   question.content = option.get('content')
                   question.is_correct = option.get('is_correct')
                   db.session.flush()
                   
        
        db.session.commit()

        return jsonify(data)


# Create an API Endpoint for Choices of Math Questions
api.add_resource(MathChoicesAPI, '/mathopn-api') 



# Creating API Class for to manage Math Questions 
class GEASQuestionsAPI(Resource):
   
   # Retrieve questions from the database
   def get(self):
           questions = GEASQuestions.query.all()
           geas_questions = [{"question_id":question.id, "question":question.content} for question in questions]
           data = {"geas_questions":geas_questions}
           print('Question retrieve from the database successfully')
           return jsonify(data)
           

   # Fetching new math questions from the administrator 
   def post(self):
            print('hehe')
            global field_labels
                
            if request.data:
                 data = request.json
                 max_question_id = db.session.query(func.max(GEASQuestions.id)).scalar()
                 max_option_id = db.session.query(func.max(GEASOptions.id)).scalar()
                 question = data.get('content')
                 options = data.get('options')

                 # Set the value of max_question_id and max_option_id to 0 if their value is None (No questions is in the database)
                 if max_question_id is None:
                        max_question_id = 0

                 if max_option_id is None:
                     max_option_id = 0

                 if question:
                    
                    new_question_id = max_question_id + 1
                    new_question = GEASQuestions(id=new_question_id, content=question) 
                    db.session.add(new_question)
                    db.session.flush() 

                    if options:     
                      for option_data in options:    
                             max_option_id += 1
                             letter = option_data['letter']
                             content = option_data['content']
                             is_correct = option_data['is_correct']
                             new_option = GEASOptions(id=max_option_id, question_no=new_question_id, letter=letter, content=content, is_correct=is_correct)
                             db.session.add(new_option)
                             

                 db.session.commit()
                 return jsonify({"message":"Question added succesfully"})


   # Update questions from the database        
   def put(self):
       print("PUT request is received")
       data = request.get_json()
       update_question_id = data.get('question_id')
       new_question = data.get('q_content')
       
       update_question = GEASQuestions.query.filter_by(id=update_question_id).first()

       if update_question: 
           update_question.content = new_question   
       
       db.session.commit()

       return jsonify({"update_question_id":update_question_id, "new_question":new_question})
    

   # delete questions from the database
   def delete(self):
       delete_question_id = request.form.get('question_id')
       question = GEASQuestions.query.filter_by(id=delete_question_id).first()
     
       if delete_question_id:
           db.session.delete(question)
       
       db.session.commit()
           
       print({'message': 'Question deleted successfully'}, 200)
            

# Create an API Endpoint for Math Resource
api.add_resource(GEASQuestionsAPI, '/geasqn-api')


# Creating API Class to manage Math Choices 
class GEASChoicesAPI(Resource):

    def get(self):
        qn = GEASQuestions.query.all()
        opn = GEASOptions.query.all()
        geas_questions = [{"id":question.id, "content":question.content, "options":[{"question_no":option.question_no, "letter":option.letter, "content":option.content, "is_correct":option.is_correct} for option in opn if option.question_no == question.id]} for question in qn]
        return jsonify(geas_questions)
   

    def put(self):
        data = request.get_json()
        options = data.get('options')
        print(data)
        questions = GEASOptions.query.filter_by(question_no=data.get('question_id')).all()
        for question in questions:
            for option in options:
               if question.letter == option.get('letter'):
                   question.content = option.get('content')
                   question.is_correct = option.get('is_correct')
                   db.session.flush()
                   
        
        db.session.commit()

        return jsonify(data)


# Create an API Endpoint for Choices of Math Questions
api.add_resource(GEASChoicesAPI, '/geasopn-api') 
