from flask import Flask 
from flask_bcrypt import Bcrypt
from flask_restful import Api
from .config import Config 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Config) 
api = Api(app)
bcrypt = Bcrypt(app)

# Initializes the database
db = SQLAlchemy(app)

