from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt, set_access_cookies, set_refresh_cookies
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import requests
import os
from datetime import datetime, timedelta, timezone
from flask_session import Session
from flask import session
from app import db, limiter
from models import User, UserRole, TokenBlacklist
from utils.validators import validate_email, validate_password, verify_reset_token, generate_reset_token
from utils.security import FailedLoginTracker, SecurityMonitor, IPBlocker
from config import Config
from services.email_service import EmailService
from services.sms_service import SmsService



sms_service = SmsService()

email_service = EmailService()

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS_PROFILES = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_PROFILES



""" Register 
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(data['password']):
            return jsonify({
                'error': 'Password must be at least 8 characters long and contain uppercase, lowercase, digit and special character'
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({'error': 'Email already registered'}), 409
             
        # Handle role safely
        if data.get('role'):
            try:
                role = UserRole(data['role'].lower())
            except ValueError:
                return jsonify({'error': f"Invalid role: {data['role']}"}), 400
        else:
            role = UserRole.STUDENT
        
        # Create new user
        user = User(
            email=data['email'].lower(),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            phone=data.get('phone'),
            bio=data.get('bio')
        )
        user.set_password(data['password'])

        
        db.session.add(user)
        db.session.commit()
        email_service.send_welcome_email(user)

        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response_data = {
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        email_service.send_welcome_email(user)
        # ✅ jsonify makes it a Response object
        response = jsonify(response_data)

        # ✅ Attach cookies properly
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response, 201 
        
    except Exception as e:
        db.session.rollback()
        # Always return JSON response on error
        return jsonify({'error': str(e)}), 500
"""
def send_otp(phone):
       # Send OTP via Twilio
    from services.sms_service import SmsService
    sms = SmsService()
    otp_status = sms.send_otp(phone)
    return otp_status

@auth_bp.route('/register', methods=['POST'])
# @limiter.limit("5 per hour")
def register():
    try:
        data = request.get_json()

        required_fields = ['email', 'password', 'first_name', 'last_name', 'phone']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        # Validations
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        if not validate_password(data['password']):
            return jsonify({'error': 'Weak password'}), 400

        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({'error': 'Email already registered'}), 409

             
        # Handle role safely
        if data.get('role'):
            try:
                role = UserRole(data['role'].lower())
            except ValueError:
                return jsonify({'error': f"Invalid role: {data['role']}"}), 400
        else:
            role = UserRole.STUDENT

        # Save temporarily in session
        # session.permanent = True  # Extend session lifetime (default 31 days)
        # session.permanent = True
        # session.modified = True  # ADD THIS
        
        # Save temporarily in session
        # session.clear()  # Clear any old data first
        session.permanent = True
        session['pending_user'] = {
            'email': data['email'].lower(),
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'password': data['password'],
            'phone': data['phone'],
            'bio': data.get('bio'),
            'role': role.value,
            'otp_expiry': (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        }
        session.modified = True  # ADD THIS LINE
        _ = session['pending_user']  # Force serialization - ADD THIS LINE

        print("=" * 50)
        print("REGISTER ROUTE - SESSION DEBUG")
        print("=" * 50)
        print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'No SID'}")
        print(f"Session keys: {list(session.keys())}")
        print(f"Saved to session: {session.get('pending_user')}")
        print(f"Session modified: {session.modified}")
        print("=" * 50)
        
        
        
        # Send OTP via Twilio
        # from services.sms_service import SmsService
        # sms = SmsService()
        # otp_status = sms.send_otp(data['phone'])

        otp_status = send_otp(data['phone'])

        if otp_status != "pending":
            session.pop('pending_user', None)  # clear if failed
            return jsonify({'error': 'Failed to send OTP'}), 500

        return jsonify({
            'message': f'OTP sent to {data["phone"]}',
            'status': 'OTP_SENT',
            'next': 'api/v1/auth/verify-otp',
            'session-data': session.get('pending_user')
        }), 200

    except Exception as e:
        session.pop('pending_user', None)
        return jsonify({'error': str(e)}), 500
    

@auth_bp.route('/verify-otp', methods=['POST'])
# @limiter.limit("10 per hour")
def verify_otp():
    try:
        print("=" * 50)
        print("VERIFY OTP ROUTE HIT")
        print("=" * 50)
        
        # Debug session information
        print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'No SID'}")
        print(f"Session keys: {list(session.keys())}")
        print(f"Session data: {dict(session)}")
        print(f"Request cookies: {request.cookies}")
        
        data = request.get_json()
        otp = data.get('otp')
        pending_user = session.get('pending_user')
        print(f"pending_user from session: {pending_user}")
        print("=" * 50)

        if not pending_user:
            return jsonify({'error': 'Session expired or no user data found'}), 400

        phone = pending_user.get('phone')  # Now safe

        # Check expiry
        otp_expiry_str = pending_user.get('otp_expiry')
        if otp_expiry_str:
            otp_expiry = datetime.fromisoformat(otp_expiry_str)
            if datetime.now(timezone.utc) > otp_expiry:
                session.pop('pending_user', None)
                return jsonify({'error': 'Session expired. Please register again.'}), 400

        
        if not phone or not otp:
            return jsonify({'error': 'Phone and OTP required'}), 400


        if not pending_user:
            return jsonify({'error': 'Session expired or no user data found'}), 400

        # Verify OTP with Twilio
      
        result = sms_service.verify_otp(phone, otp)

        if result != 'approved':
            return jsonify({'error': 'Invalid o`r expired OTP'}), 400
        
        role = pending_user.get('role', 'student')

        # OTP verified → create user
        user = User(
            email=pending_user['email'],
            first_name=pending_user['first_name'],
            last_name=pending_user['last_name'],
            phone=pending_user['phone'],
            bio=pending_user.get('bio'),
            role=UserRole(role.lower())

        )
        user.set_password(pending_user['password'])
        db.session.add(user)
        db.session.commit()
        email_service.send_welcome_email(user)


        # Clear session
        session.pop('pending_user', None)

        # Tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = jsonify({
            'message': 'Registration successful!',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 201

    except Exception as e:
        db.session.rollback()
        session.pop('pending_user', None)
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/resend-otp', methods=['POST'])
@limiter.limit("3 per hour")
def resend_otp():
    try:
        pending_user = session.get('pending_user')
        if not pending_user:
            return jsonify({'error': 'Session expired or no user data found'}), 400
            
        phone = pending_user.get('phone')
        if not phone:
            return jsonify({'error': 'Phone number not found in session'}), 400

        # Check expiry
        otp_expiry_str = pending_user.get('otp_expiry')
        if otp_expiry_str:
            otp_expiry = datetime.fromisoformat(otp_expiry_str)
            if datetime.now(timezone.utc) > otp_expiry:
                session.pop('pending_user', None)
                return jsonify({'error': 'Session expired. Please register again.'}), 400

        otp_status = send_otp(phone=phone)

        if otp_status != "pending":
            # session.pop('pending_user', None)  # Optional: Decide if you want to clear session on failure
            return jsonify({'error': 'Failed to send OTP'}), 500

        return jsonify({
            'message': f'OTP sent to {phone}',
            'status': 'OTP_SENT',
            'session-data': session.get('pending_user')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500




"""  Login  """
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per 15 minutes")
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower()
        
        # Check if IP is blocked
        is_blocked, seconds_remaining = IPBlocker.is_ip_blocked()
        if is_blocked:
            return jsonify({
                'error': 'Too many failed attempts. Please try again later.',
                'retry_after': seconds_remaining
            }), 429
        
        # Check if account is locked
        is_locked, seconds_remaining = FailedLoginTracker.is_blocked(email=email)
        if is_locked:
            return jsonify({
                'error': 'Account temporarily locked due to multiple failed login attempts.',
                'retry_after': seconds_remaining
            }), 429
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(data['password']):
            # Record failed attempt
            FailedLoginTracker.record_failed_attempt(email=email)
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Reset failed attempts on successful login
        FailedLoginTracker.reset_attempts(email=email)
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
""" Refresh Token """
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))  # convert back to int
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or deactivated'}), 404
        
        new_token = create_access_token(identity=str(user.id))  # must be string
        
        return jsonify({
            'access_token': new_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

""" Logout  """
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']
        
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(jti=jti)
        db.session.add(blacklisted_token)
        db.session.commit()
        
        return jsonify({'message': 'Successfully logged out'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

""" Change Password  """
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Check current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        if not validate_password(data['new_password']):
            return jsonify({'error': 'New password must be at least 8 characters long and contain uppercase, lowercase, digit and special character'}), 400
        
        # Update password
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

""" Get Current Details   """
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500





GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
# Step 2: Function to verify Google ID token
def verify_google_token(token):
    try:
        response = requests.get(
            f'https://oauth2.googleapis.com/tokeninfo?id_token={token}',
            timeout=5  # Add timeout
        )
        
        if response.status_code != 200:
            print(f"Google token verification failed: {response.text}")
            return None
            
        user_info = response.json()

        # Check for required fields
        if 'aud' not in user_info or 'email' not in user_info:
            print("Missing required fields in token response")
            return None

        # Verify audience (use GOOGLE_CLIENT_ID directly)
        if user_info['aud'] != GOOGLE_CLIENT_ID:
            print(f"Token audience mismatch: {user_info['aud']}")
            return None

        return user_info
        
    except requests.exceptions.Timeout:
        print("Google token verification timeout")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None


# Step 3: Route to handle Google login
@auth_bp.route('/google', methods=['POST'])
@limiter.limit("20 per hour")
def google_login():
    try:
        data = request.get_json()
        google_token = data.get("token")

        if not google_token:
            return jsonify({"error": "Token is missing"}), 400

        user_info = verify_google_token(google_token)
        if not user_info:
            return jsonify({"error": "Invalid token"}), 401

        email = user_info.get("email")
        google_id = user_info.get("sub")
        
        # Determine role BEFORE querying
        client_type = data.get("client_type", "student")  # Default to student
        user_role = UserRole.STUDENT if client_type == "student" else UserRole.ADMIN
        
        # Find or create user (SINGLE query)
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                email=email,
                first_name=user_info.get("given_name"),
                last_name=user_info.get("family_name"),
                profile_picture=user_info.get("picture"),
                email_verified=user_info.get("email_verified", False),
                role=user_role,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Optional: Update existing user's info
            user.profile_picture = user_info.get("picture")
            user.email_verified = user_info.get("email_verified", False)
            db.session.commit()
        
        # Create access token
        access_token = create_access_token(
            identity=str(user.id),  # Convert to string for JWT
            additional_claims={
                "email": email,
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            }
        )

        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()  # Include user data in response
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Google login error: {str(e)}")
        return jsonify({"error": "Login failed"}), 500

    
@auth_bp.route('/send-token', methods=['POST'])
@limiter.limit("3 per hour")
def send_reset_token():
    email = request.get_json().get("email")
    if not email:
        return jsonify({"error": "Email is missing"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    token = generate_reset_token(user)
    return jsonify({"token": token}), 200


@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    try:
        token = request.args.get("token", None)
        data = request.get_json()
        new_password = data.get("password")

        if not token:
            return jsonify({"error": "Token is missing"}), 400

        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        # Verify token
        email = verify_reset_token(token=token) 

        if not email:
            return jsonify({"error": "Invalid or expired token"}), 400

        # Get user from DB
        user = User.query.filter_by(email=email).first()
        print("user:",user)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Hash password
        from werkzeug.security import generate_password_hash
        user.password = user.set_password(new_password)

        db.session.commit()

        return jsonify({"message": "Password updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
