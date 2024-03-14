
from flask_migrate import Migrate
from flask import Flask
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy

template_dir = Path('../templates')
app = Flask(__name__, template_folder=template_dir)
app.static_folder = Path('../static')

app.config['SECRET_KEY'] = 'todolist'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/todolist_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import modelos
from . import routes
