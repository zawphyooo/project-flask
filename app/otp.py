from app import db
import string
import datetime
import random


# Function to generate a random OTP
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Function to store OTP in the database
def store_otp(user_id, otp):
    created_at = datetime.datetime.now()
    db.execute("INSERT INTO otps (user_id, otp, created_at) VALUES (?, ?, ?)", user_id, otp, created_at)


# Function to validate OTP
def validate_otp(user_id, input_otp, expiry_minutes=5):
    result = db.execute("SELECT otp, created_at FROM otps WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
    
    if result:
        created_at = result[0]["created_at"]
        otp = result[0]["otp"]
        created_at = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        if otp == input_otp and (now - created_at).total_seconds() <= expiry_minutes * 60:
            return True
    return False