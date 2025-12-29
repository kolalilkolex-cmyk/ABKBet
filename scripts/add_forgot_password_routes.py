"""Add forgot password routes to auth_routes.py"""

routes_to_add = """
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    \"\"\"Request password reset\"\"\"
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
    \"\"\"Reset password with token\"\"\"
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
"""

auth_routes_path = r"C:\Users\HP\OneDrive\Documents\ABKBet\app\routes\auth_routes.py"

with open(auth_routes_path, 'a', encoding='utf-8') as f:
    f.write(routes_to_add)

print("✅ Forgot password routes added successfully!")
