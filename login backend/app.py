from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from models import db, User, OTP
from otp_utils import generate_otp, hash_otp, verify_otp, otp_expiry

app = Flask(__name__)
app.secret_key = 'your-very-secret-key-12345'  # Set a strong, random key in production
CORS(app, supports_credentials=True)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# ---------------- SEND OTP ----------------
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    mobile = data.get("mobile")
    email = data.get("email")

    if not mobile:
        return jsonify({"error": "Mobile number required"}), 400

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    # Remove old OTP if exists
    OTP.query.filter_by(mobile=mobile).delete()

    new_otp = OTP(
        mobile=mobile,
        otp_hash=otp_hash,
        expires_at=otp_expiry()
    )

    db.session.add(new_otp)
    db.session.commit()

    # For hackathon/testing
    print("OTP:", otp)

    return jsonify({"message": "OTP sent successfully"}), 200


# ---------------- VERIFY OTP ----------------
@app.route("/verify-otp", methods=["POST"])
def verify_otp_api():
    data = request.json
    mobile = data.get("mobile")
    otp = data.get("otp")
    email = data.get("email")

    otp_record = OTP.query.filter_by(mobile=mobile).first()

    if not otp_record:
        return jsonify({"error": "OTP not found"}), 400

    if otp_record.expires_at < otp_record.expires_at.utcnow():
        return jsonify({"error": "OTP expired"}), 400

    if not verify_otp(otp, otp_record.otp_hash):
        return jsonify({"error": "Invalid OTP"}), 400

    # Create user if not exists (signup)
    user = User.query.filter_by(mobile=mobile).first()
    if not user:
        user = User(
            mobile=mobile,
            email=email,
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()

    return jsonify({"message": "Login successful"}), 200


# ---------------- RUN SERVER ----------------
# ---------------- RUN SERVER ----------------

# ---------------- CAPTCHA ENDPOINTS ----------------
import io
from PIL import Image, ImageDraw, ImageFont
import random, string
from flask import session

@app.route('/generate-captcha')
def generate_captcha():
    # Generate random text
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session['captcha'] = captcha_text
    # Create image
    img = Image.new('RGB', (150, 50), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 36)
    except:
        font = ImageFont.load_default()
    d.text((10, 5), captcha_text, font=font, fill=(30, 30, 60))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=False)

@app.route('/verify-captcha', methods=['POST'])
def verify_captcha():
    data = request.json
    user_captcha = data.get('captcha', '').strip().upper()
    real_captcha = session.get('captcha', '').upper()
    if user_captcha == real_captcha and real_captcha:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid captcha'}), 400

if __name__ == "__main__":
    app.run(debug=True)