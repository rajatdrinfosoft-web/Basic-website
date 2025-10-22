from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.String(20), index=True)
    rating = db.Column(db.String(10))
    image = db.Column(db.String(255))
    duration = db.Column(db.String(50), index=True)
    destination = db.Column(db.String(100), index=True)
    best_time = db.Column(db.String(100))
    group_size = db.Column(db.String(50))
    overview = db.Column(db.Text)
    itinerary = db.Column(db.Text)
    inclusions = db.Column(db.Text)
    exclusions = db.Column(db.Text)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50))
    destination = db.Column(db.String(100))
    image = db.Column(db.String(255))
    link = db.Column(db.String(255))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
