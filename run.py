from app import app
from app import apimodels, config, forms, models, routes, utils

if __name__ == '__main__':
    app.run(host='localhost', debug=True)

