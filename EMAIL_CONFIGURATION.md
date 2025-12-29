# Email Setup Guide for ABKBet

## Current Status
✅ Registration and login work WITHOUT email
❌ Confirmation emails are NOT being sent (SMTP not configured)

## Why Emails Aren't Sending
The app requires SMTP credentials to send emails. Currently, the `.env` file has empty SMTP_USERNAME and SMTP_PASSWORD, so emails are only logged to the console instead of being sent.

## How to Enable Email Sending

### Option 1: Gmail (Recommended for Testing)

1. **Create/Use a Gmail Account**
   - Go to https://gmail.com
   - Use an existing Gmail or create a new one

2. **Enable 2-Factor Authentication**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

3. **Create an App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Click "Generate"
   - Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)

4. **Update .env File**
   Open `C:\Users\HP\OneDrive\Documents\ABKBet\.env` and update:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop  (paste the app password without spaces)
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

5. **Restart the Flask App**
   - Stop the running app (Ctrl+C)
   - Run: `python run.py`

### Option 2: Outlook/Hotmail

Update `.env`:
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-outlook-password
SMTP_FROM_EMAIL=your-email@outlook.com
```

### Option 3: SendGrid (Best for Production)

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create an API Key
3. Update `.env`:
   ```
   SMTP_SERVER=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USERNAME=apikey
   SMTP_PASSWORD=your-sendgrid-api-key
   SMTP_FROM_EMAIL=noreply@yourdomain.com
   ```

### Option 4: Keep Emails Disabled (Development Only)

If you don't need emails right now:
- Leave SMTP_USERNAME and SMTP_PASSWORD empty
- Users can still register and login
- Email confirmations will be logged to console/logs instead
- Check `logs/run_app.log` to see what emails would have been sent

## Testing Email Setup

1. **Check Logs**
   After registration, check the terminal output or `logs/run_app.log`:
   - If configured: "Email sent successfully to..."
   - If not configured: "Email not configured. Would have sent..."

2. **Test Registration**
   - Register a new user with a real email address
   - Check your inbox (and spam folder!)
   - You should receive a "Welcome to ABKBet" email

3. **Test Password Change**
   - Login and change your password
   - Check for "Password Changed Successfully" email

## Troubleshooting

### Gmail "Less secure app" error
- Make sure you're using an **App Password**, not your regular Gmail password
- 2-Factor Authentication must be enabled first

### Connection timeout
- Check if your firewall is blocking port 587
- Try port 465 with SSL instead (update SMTP_PORT=465)

### "Authentication failed"
- Double-check your username and password
- Remove any spaces from the app password
- For Gmail, use the full email as username

### Still not working?
Check the logs at `C:\Users\HP\OneDrive\Documents\ABKBet\logs\run_app.log` for detailed error messages.

## Email Templates

The app sends two types of emails:

1. **Registration Email** - Sent when a new user signs up
   - Welcome message
   - Account confirmation
   - Getting started tips

2. **Password Change Email** - Sent when password is changed
   - Confirmation of change
   - Security warning if it wasn't you
   - Security tips

## Production Recommendations

For production deployment:
1. Use a dedicated email service (SendGrid, AWS SES, Mailgun)
2. Use a custom domain email (noreply@yourdomain.com)
3. Set up SPF, DKIM, and DMARC records
4. Monitor email delivery rates
5. Handle bounces and complaints
6. Never use personal Gmail for production

## Questions?

Email functionality is **optional** for development. The app works perfectly without it - users just won't receive confirmation emails.
