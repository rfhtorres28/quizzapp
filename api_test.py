from flask import Flask, jsonify, request
from flask_restful import Api, Resource



app = Flask(__name__) 
api = Api(app)


database = {1:{"name":"Ronnier"}, 2:{"name":"Princess"}}


class Names(Resource):

    def get(self, n):
      if n in database.keys():
         return database[n]
      else:
         return jsonify({"message":"Data doesnt exist"})
      
    def put(self, n):
       data = request.json
       database[n] = data
       return database





    

class AddName(Resource):

    def get(self):
       return database

    def post(self):
       data = request.json # returns a dictionary
       nameId = len(database.keys())+1
       database[nameId] = data
       
       return database

    



api.add_resource(Names, "/<int:n>")
api.add_resource(AddName, "/names")






if __name__ == "__main__":
    app.run(debug=True)