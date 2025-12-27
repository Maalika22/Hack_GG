# Email Configuration Guide

## Quick Setup (Recommended)

### Option 1: Use Setup Script (Easiest)
```powershell
.\setup_email.ps1
```

This script will guide you through setting up email credentials.

### Option 2: Manual Setup

#### For Gmail:

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "GearGuard" as the name
   - Copy the 16-character password (format: `abcd efgh ijkl mnop`)

3. **Set Environment Variables** (Windows PowerShell):
   ```powershell
   $env:MAIL_USERNAME="your-email@gmail.com"
   $env:MAIL_PASSWORD="abcd efgh ijkl mnop"
   ```

4. **Verify Configuration**:
   ```bash
   python test_email_config.py
   ```

#### For Other Email Providers:

**Outlook/Hotmail:**
```powershell
$env:MAIL_SERVER="smtp-mail.outlook.com"
$env:MAIL_PORT="587"
$env:MAIL_USERNAME="your-email@outlook.com"
$env:MAIL_PASSWORD="your-password"
```

**Yahoo:**
```powershell
$env:MAIL_SERVER="smtp.mail.yahoo.com"
$env:MAIL_PORT="587"
$env:MAIL_USERNAME="your-email@yahoo.com"
$env:MAIL_PASSWORD="your-app-password"
```

## Making Configuration Permanent

### Option 1: PowerShell Profile (Recommended)
Add to your PowerShell profile (`$PROFILE`):
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-app-password"
```

### Option 2: System Environment Variables
1. Open System Properties → Environment Variables
2. Add `MAIL_USERNAME` and `MAIL_PASSWORD` to User variables
3. Restart your terminal/application

## Testing Email

### Test Configuration:
```bash
python test_email_config.py
```

### Test Email Sending:
```bash
python send_test_email.py
```

## Troubleshooting

### "Email configuration missing" Error
- **Solution**: Set `MAIL_USERNAME` and `MAIL_PASSWORD` environment variables
- Run `.\setup_email.ps1` for guided setup

### Gmail "Less secure app" Error
- **Solution**: Gmail no longer supports "less secure apps"
- **Must use**: App Passwords with 2FA enabled
- Generate App Password at: https://myaccount.google.com/apppasswords

### "Authentication failed" Error
- **For Gmail**: Make sure you're using App Password, not regular password
- **For others**: Check your SMTP credentials

### Emails Not Arriving
1. Check spam/junk folder
2. Verify email address is correct
3. Check application logs for errors
4. Test with `send_test_email.py`

## Email Features

Once configured, the system sends:
- ✅ **OTP for Email Verification** (registration)
- ✅ **OTP for Login** (if email not verified)
- ✅ **Login Notification** (after successful login)
- ✅ **Password Reset OTP** (forgot password)
- ✅ **Work Allocation Emails** (to workers)
- ✅ **Vendor Notifications** (to third-party users)

## Fallback Mode

If email is not configured, OTP codes will be displayed in the console/terminal for testing purposes.
