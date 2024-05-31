

class Config:
    SECRET_KEY = 'Tootsie@2714'


    # Database configuration
    username = 'ronnierflask'
    password = 'Tootsie@1430'
    port = '3306'
    host = 'localhost'
    database_name = 'quizapp'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}?charset=utf8mb4'


