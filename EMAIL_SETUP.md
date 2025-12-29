# Email Notifications Setup

## Overview

ABKBet now sends email confirmations for:
1. **User Registration** - Welcome email with bonus information
2. **Password Changes** - Security confirmation email

If email is not configured, the system will log the emails instead and continue working normally.

## Features

### Registration Email
- Welcome message with username
- Account benefits and features
- Special bonus offer (100% first deposit)
- Link to login and start betting

### Password Change Email
- Confirmation of password update
- Security alert if user didn't make the change
- Security tips and best practices
- Link back to login

## Setup Instructions

### Step 1: Copy Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 2: Configure Email Provider

Edit `.env` and add your email settings:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=ABKBet
```

### Step 3: Get Email Credentials

#### For Gmail (Recommended for Testing):

1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification (enable if not already)
3. Go to App Passwords: https://myaccount.google.com/apppasswords
4. Generate a new app password for "Mail"
5. Copy the 16-character password
6. Use this as `SMTP_PASSWORD` in `.env`

**Important:** Use an App Password, NOT your regular Gmail password!

#### For Other Providers:

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Yahoo Mail:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

**SendGrid (Production Recommended):**
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### Step 4: Test the Setup

1. Start the server:
   ```bash
   python run.py
   ```

2. Register a new user with a real email address

3. Check your inbox for the welcome email

4. Try changing your password and check for the confirmation email

## Troubleshooting

### Email Not Sending

**Check logs:** Look in `logs/run_app.log` for email errors

**Common issues:**

1. **Invalid credentials**
   - Make sure you're using an App Password for Gmail
   - Check username/password are correct

2. **SMTP blocked**
   - Some networks block SMTP ports
   - Try using port 465 (SSL) instead of 587 (TLS)

3. **Less secure apps**
   - Gmail requires App Passwords with 2FA enabled
   - Don't try to use "Allow less secure apps" (deprecated)

### Email Goes to Spam

- Add proper SPF/DKIM records to your domain (for production)
- Use a professional email service like SendGrid or AWS SES
- Avoid using personal Gmail for production

### Testing Without Real Email

If you don't want to configure email, the system will work fine without it:
- Emails will be logged to console/log files
- Users won't receive emails but can still use the platform
- Success messages will still appear in the UI

## Production Recommendations

For production deployment, use a dedicated email service:

1. **SendGrid** - 100 emails/day free
2. **AWS SES** - $0.10 per 1,000 emails
3. **Mailgun** - 5,000 emails/month free
4. **Postmark** - 100 emails/month free

These services provide:
- Better deliverability
- Email analytics
- Template management
- Higher sending limits
- Better spam protection

## Email Templates

Email templates are defined in `app/utils/email.py`:
- `send_registration_email()` - Welcome email template
- `send_password_change_email()` - Password change template

Both templates include:
- Professional HTML styling
- Mobile-responsive design
- Plain text fallback
- Brand colors and logo support

You can customize these templates by editing the HTML in `app/utils/email.py`.

## Security Notes

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use environment variables** - Don't hardcode email passwords
3. **Use App Passwords** - Never use your main account password
4. **Enable 2FA** - Required for Gmail App Passwords
5. **Rotate passwords** - Change email passwords periodically
6. **Monitor logs** - Check for failed authentication attempts

## API Response Changes

The authentication endpoints now return additional fields:

### Registration Response
```json
{
  "message": "Registration successful! Welcome to ABKBet...",
  "access_token": "...",
  "user": {...},
  "show_success_message": true
}
```

### Password Change Response
```json
{
  "message": "Password changed successfully! Check your email...",
  "show_success_message": true
}
```

The `show_success_message` flag tells the frontend to display a prominent success notification.
