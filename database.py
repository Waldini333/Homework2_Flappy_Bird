from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flappy.db"
db = SQLAlchemy(app)

class Player(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable = False)
    score = db.Column(db.Integer, unique=False, nullable=False)



db.create_all()


