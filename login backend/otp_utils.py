import random
import bcrypt
from datetime import datetime, timedelta

# Generate 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Convert OTP into hash
def hash_otp(otp):
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt())

# Check OTP against hash
def verify_otp(otp, otp_hash):
    return bcrypt.checkpw(otp.encode(), otp_hash)

# OTP expiry time (5 minutes)
def otp_expiry():
    return datetime.utcnow() + timedelta(minutes=5)