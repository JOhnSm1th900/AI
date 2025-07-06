from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# creating a Flask-SQLAlchemy extension instance without yet binding it to an app.

db = SQLAlchemy()

# UserMixin gives you common login-related methods (is_authenticated, etc.).
# set_password & check_password utilize Werkzeug's secure hashing functions—industry standard—and are recommended in tutorials like Miguel Grinberg’s Flask Mega Tutorial

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

# result stores the predicted class (integer).
# proba with PickleType stores probability arrays—SQLAlchemy auto-serializes/deserializes them for you
# timestamp logs when the prediction was created.
# user_id associates each prediction with the user who made it.

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer, nullable=False)
    proba = db.Column(db.PickleType, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)