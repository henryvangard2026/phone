#
# user database:
#
# - adding a database to manager the users
#
# DATE:  1/25/26
#
# TODO:
#
# - brain storming phase, no implementation yet.
#


from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from flask_login import UserMixin

# Flask and login related modules

from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt


# User class
class User(Base, UserMixin):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name} ({self.username})>"


app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Required for session signing
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Where to send users if they aren't logged in

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))
