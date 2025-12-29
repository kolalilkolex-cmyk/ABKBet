"""
Email utility for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_email(to_email, subject, body_html, body_text=None):
    """
    Send an email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML body content
        body_text: Plain text body (optional, fallback)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get email configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
        from_name = os.getenv('SMTP_FROM_NAME', 'ABKBet')
        
        # Skip sending if email is not configured
        if not smtp_username or not smtp_password:
            logger.warning(f"Email not configured. Would have sent: {subject} to {to_email}")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Attach plain text and HTML versions
        if body_text:
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(body_html, 'html')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_registration_email(user_email, username):
    """
    Send welcome email after successful registration
    
    Args:
        user_email: User's email address
        username: User's username
    """
    subject = "Welcome to ABKBet - Registration Successful!"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to ABKBet!</h1>
            </div>
            <div class="content">
                <h2>Hello {username},</h2>
                <p>Congratulations! Your account has been successfully created.</p>
                <p>You can now:</p>
                <ul>
                    <li>✅ Fund your wallet and start betting</li>
                    <li>✅ Place bets on multiple markets (1X2, Over/Under, Correct Score, and more)</li>
                    <li>✅ Track your bets and winnings in real-time</li>
                    <li>✅ Withdraw your winnings to Bitcoin</li>
                </ul>
                <p style="text-align: center;">
                    <a href="http://127.0.0.1:5000" class="button">Start Betting Now</a>
                </p>
                <p><strong>🎁 Special Offer:</strong> Get up to 100% bonus on your first deposit!</p>
                <p>If you have any questions, feel free to contact our support team.</p>
                <p>Best regards,<br>The ABKBet Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>&copy; 2025 ABKBet. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    Welcome to ABKBet!
    
    Hello {username},
    
    Congratulations! Your account has been successfully created.
    
    You can now:
    - Fund your wallet and start betting
    - Place bets on multiple markets
    - Track your bets and winnings in real-time
    - Withdraw your winnings to Bitcoin
    
    Special Offer: Get up to 100% bonus on your first deposit!
    
    Visit: http://127.0.0.1:5000
    
    Best regards,
    The ABKBet Team
    """
    
    return send_email(user_email, subject, body_html, body_text)


def send_password_change_email(user_email, username):
    """
    Send confirmation email after password change
    
    Args:
        user_email: User's email address
        username: User's username
    """
    subject = "Password Changed Successfully - ABKBet"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
            .alert {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
            .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Password Changed</h1>
            </div>
            <div class="content">
                <h2>Hello {username},</h2>
                <p>This email confirms that your password has been successfully changed.</p>
                <div class="alert">
                    <strong>⚠️ Security Notice:</strong> If you did not make this change, please contact our support team immediately and secure your account.
                </div>
                <p>Your account security is important to us. Here are some tips:</p>
                <ul>
                    <li>Never share your password with anyone</li>
                    <li>Use a strong, unique password</li>
                    <li>Enable two-factor authentication if available</li>
                    <li>Regularly update your password</li>
                </ul>
                <p style="text-align: center;">
                    <a href="http://127.0.0.1:5000" class="button">Login to Your Account</a>
                </p>
                <p>If you need any assistance, our support team is here to help.</p>
                <p>Best regards,<br>The ABKBet Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>&copy; 2025 ABKBet. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    Password Changed - ABKBet
    
    Hello {username},
    
    This email confirms that your password has been successfully changed.
    
    SECURITY NOTICE: If you did not make this change, please contact our support team immediately.
    
    Security Tips:
    - Never share your password with anyone
    - Use a strong, unique password
    - Enable two-factor authentication if available
    - Regularly update your password
    
    Visit: http://127.0.0.1:5000
    
    Best regards,
    The ABKBet Team
    """
    
    return send_email(user_email, subject, body_html, body_text)

def send_password_reset_email(user_email, username, reset_token):
    """
    Send password reset email with reset link
    
    Args:
        user_email: User's email address
        username: User's username
        reset_token: Password reset token
    """
    subject = "Password Reset Request - ABKBet"
    
    # In production, this should be your actual domain
    reset_link = f"http://127.0.0.1:5000/reset-password?token={reset_token}"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .alert {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }}
            .code {{ font-family: monospace; background: #e2e8f0; padding: 10px; border-radius: 5px; font-size: 16px; letter-spacing: 2px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1> Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Hello {username},</h2>
                <p>We received a request to reset your password for your ABKBet account.</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Your Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p class="code">{reset_link}</p>
                <div class="alert">
                    <strong> Important:</strong> This link will expire in 1 hour for security reasons.
                </div>
                <p><strong>Didn't request a password reset?</strong></p>
                <p>If you didn't request this, you can safely ignore this email. Your password will remain unchanged.</p>
                <p>For security reasons:</p>
                <ul>
                    <li>Never share this link with anyone</li>
                    <li>ABKBet staff will never ask for your password</li>
                    <li>Always verify the sender's email address</li>
                </ul>
                <p>Best regards,<br>The ABKBet Team</p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>&copy; 2025 ABKBet. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    Password Reset Request - ABKBet
    
    Hello {username},
    
    We received a request to reset your password for your ABKBet account.
    
    To reset your password, visit this link:
    {reset_link}
    
    IMPORTANT: This link will expire in 1 hour for security reasons.
    
    Didn't request a password reset?
    If you didn't request this, you can safely ignore this email. Your password will remain unchanged.
    
    Security Tips:
    - Never share this link with anyone
    - ABKBet staff will never ask for your password
    - Always verify the sender's email address
    
    Best regards,
    The ABKBet Team
    """
    
    return send_email(user_email, subject, body_html, body_text)
