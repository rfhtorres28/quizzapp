from flask_login import LoginManager
from .models import UserDetails
from . import app


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return UserDetails.query.get(int(user_id))