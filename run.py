from app import app
from app import apimodels, config, forms, models, routes, utils

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)

