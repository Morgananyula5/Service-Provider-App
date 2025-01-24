from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# User model for login/signup
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_provider = db.Column(db.Boolean, default=False)

    # Relationship with the ServiceProvider (one-to-one relationship)
    provider_profile = db.relationship('ServiceProvider', uselist=False, backref='user')

# ServiceProvider model
class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_details = db.Column(db.String(500))
    service_description = db.Column(db.String(1000))
    areas_served = db.Column(db.String(500))  # List of counties or areas served
    availability = db.Column(db.String(500))
    pricing_info = db.Column(db.String(500))
    reviews = db.Column(db.String(1000))  # Review details

# Initialize the database
def init_db():
    db.create_all()
