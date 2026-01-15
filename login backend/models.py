from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create database object
db = SQLAlchemy()

# User table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# OTP table
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(15))
    otp_hash = db.Column(db.String(255))
    expires_at = db.Column(db.DateTime)