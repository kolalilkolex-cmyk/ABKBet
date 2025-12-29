from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import db, User
from app.utils.auth import hash_password, verify_password
from app.utils.decorators import token_required
import logging
from app.utils.auth import hash_password, verify_password, is_strong_password
from app.utils.email import send_registration_email, send_password_change_email, send_password_reset_email
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# --- Register ---
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400

        if not is_strong_password(password):
            return jsonify({'message': 'Password must be at least 8 characters and include uppercase, lowercase, number, and symbol'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists'}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists'}), 409

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True
        )
        db.session.add(user)
        db.session.commit()

        # Send registration confirmation email
        try:
            send_registration_email(user.email, user.username)
        except Exception as email_error:
            logger.warning(f"[Register] Failed to send email to {user.email}: {email_error}")

        access_token = create_access_token(identity=str(user.id))
        logger.info(f"[Register] New user: {username}")

        return jsonify({
            'message': 'Registration successful! Welcome to ABKBet. A confirmation email has been sent to your inbox.',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'show_success_message': True
        }), 201

    except Exception as e:
        logger.error(f"[Register] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Registration failed'}), 500

# --- Login ---
@auth_bp.route('/login', methods=['POST'])
def login():
    print("="*60)
    print("LOGIN ROUTE HIT!")
    print("="*60)
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        print(f"Username: {username}, Password length: {len(password)}")
        logger.info(f"[Login] Attempt for username: {username}")

        if not username or not password:
            logger.warning(f"[Login] Missing credentials")
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            logger.warning(f"[Login] User not found: {username}")
            return jsonify({'message': 'Invalid credentials'}), 401
            
        if not verify_password(user.password_hash, password):
            logger.warning(f"[Login] Invalid password for: {username}")
            return jsonify({'message': 'Invalid credentials'}), 401

        if not user.is_active:
            logger.warning(f"[Login] Suspended account: {username}")
            return jsonify({'message': 'Your account has been suspended. Please contact support.'}), 403

        access_token = create_access_token(identity=str(user.id))
        logger.info(f"[Login] Success for user: {username}")

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'balance': user.balance,
                'is_admin': user.is_admin
            }
        }), 200

    except Exception as e:
        logger.error(f"[Login] Error: {e}", exc_info=True)
        return jsonify({'message': 'Login failed'}), 500

# --- Profile ---
@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(user):
    try:
        wallet_info = {
            'bitcoin_address': user.wallet.bitcoin_address
        } if user.wallet else None

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'balance': user.balance,
                'created_at': user.created_at.isoformat(),
                'wallet': wallet_info
            }
        }), 200

    except Exception as e:
        logger.error(f"[Profile] Error for user_id={user.id}: {e}")
        return jsonify({'message': 'Profile fetch failed'}), 500

# --- Change Password ---
@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(user):
    try:
        data = request.get_json() or {}
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return jsonify({'message': 'Missing required fields'}), 400

        if not verify_password(user.password_hash, current_password):
            return jsonify({'message': 'Incorrect current password'}), 401

        if not is_strong_password(new_password):
            return jsonify({'message': 'New password is too weak. Use at least 8 characters with uppercase, lowercase, number, and symbol.'}), 400

        user.password_hash = hash_password(new_password)
        db.session.commit()

        # Send password change confirmation email
        try:
            send_password_change_email(user.email, user.username)
        except Exception as email_error:
            logger.warning(f"[Change Password] Failed to send email to {user.email}: {email_error}")

        logger.info(f"[Change Password] User: {user.username}")
        return jsonify({
            'message': 'Password changed successfully! A confirmation email has been sent to your inbox.',
            'show_success_message': True
        }), 200

    except Exception as e:
        logger.error(f"[Change Password] Error for user_id={user.id}: {e}")
        db.session.rollback()
        return jsonify({'message': 'Password change failed'}), 500
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json() or {}
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        # Always return success message to prevent email enumeration
        if not user:
            logger.info(f"[Forgot Password] Email not found: {email}")
            return jsonify({
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # Send password reset email
        try:
            send_password_reset_email(user.email, user.username, reset_token)
            logger.info(f"[Forgot Password] Reset email sent to {email}")
        except Exception as email_error:
            logger.error(f"[Forgot Password] Failed to send email to {email}: {email_error}")
            return jsonify({'message': 'Failed to send reset email. Please try again.'}), 500
        
        return jsonify({
            'message': 'If an account exists with this email, a password reset link has been sent.'
        }), 200
        
    except Exception as e:
        logger.error(f"[Forgot Password] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Password reset request failed'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json() or {}
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({'message': 'Token and new password are required'}), 400
        
        if not is_strong_password(new_password):
            return jsonify({
                'message': 'Password is too weak. Use at least 8 characters with uppercase, lowercase, number, and symbol.'
            }), 400
        
        # Find user with valid token
        user = User.query.filter_by(reset_token=token).first()
        
        if not user:
            return jsonify({'message': 'Invalid or expired reset token'}), 400
        
        # Check if token is expired
        if user.reset_token_expiry and user.reset_token_expiry < datetime.utcnow():
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            return jsonify({'message': 'Reset token has expired. Please request a new one.'}), 400
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        # Send confirmation email
        try:
            send_password_change_email(user.email, user.username)
        except Exception as email_error:
            logger.warning(f"[Reset Password] Failed to send confirmation to {user.email}: {email_error}")
        
        logger.info(f"[Reset Password] Password reset for user: {user.username}")
        return jsonify({'message': 'Password reset successfully! You can now login with your new password.'}), 200
        
    except Exception as e:
        logger.error(f"[Reset Password] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Password reset failed'}), 500
