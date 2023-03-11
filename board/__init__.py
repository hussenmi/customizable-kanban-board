from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "011d730ab92fc7e8536019bfdb33d5160f6fc7d03dd70ea01929130f129206cf"   # this and the database URI should technically be in an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///kanban.db"

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from board import urls