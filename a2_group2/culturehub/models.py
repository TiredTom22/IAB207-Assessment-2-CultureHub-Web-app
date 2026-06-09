from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    events = db.relationship('Event', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    bio = db.Column(db.Text, nullable=True)  # Optional field for user biography
    language = db.Column(db.String(255), nullable=True)  # Optional field for user's preferred language
    cultural_interests = db.Column(db.String(255), nullable=True)  # Optional field for user's cultural interests
    created_at = db.Column(db.DateTime, default=datetime.now)  # Timestamp for when the user account was created

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Open')
    tickets_available = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    acknowledgement  = db.Column(db.String(20), default='none')
    acknowledgement_text = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='event', lazy=True)
    orders = db.relationship('Order', backref='event', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

