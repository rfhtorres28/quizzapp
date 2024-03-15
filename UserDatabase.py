from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin 


username = 'root'
password = 'Toootsie@1430'
port = '3306'
host = 'localhost'
database_name = 'user'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}'

db = SQLAlchemy(app)