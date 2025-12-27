# Company-Based Email System

## Overview
The system now sends OTP and notification emails from each company's configured email address, rather than a single global email.

## Features Implemented

### 1. Company Email Configuration
- Each company can have its own SMTP email configuration
- Admin can configure email settings per company
- Fields added to Company model:
  - `smtp_server` - SMTP server address (default: smtp.gmail.com)
  - `smtp_port` - SMTP port (default: 587)
  - `smtp_use_tls` - Use TLS encryption (recommended)
  - `smtp_use_ssl` - Use SSL encryption
  - `smtp_username` - Email address for sending
  - `smtp_password` - Email password or App Password
  - `smtp_sender_name` - Display name in emails

### 2. Email Sending Logic
- **OTP Emails**: Sent from the user/worker's company email
- **Login Notifications**: Sent from the user's company email
- **Work Allocation Emails**: Sent from worker's company email
- **Vendor Notifications**: Sent from admin's company email

### 3. Fallback Mechanism
- If company doesn't have email configured, falls back to global email config
- If global email also not configured, OTP shown in console

## How to Configure

### Step 1: Access Company Management
1. Login as Admin
2. Go to **Admin → Companies**
3. Click **Edit** on the company you want to configure

### Step 2: Configure Email Settings
1. Scroll to **Email Configuration** section
2. Fill in the following:
   - **SMTP Server**: `smtp.gmail.com` (for Gmail)
   - **SMTP Port**: `587` (for Gmail with TLS)
   - **SMTP Username**: Company email address (e.g., `company@gmail.com`)
   - **SMTP Password**: App Password (for Gmail) or regular password
   - **Sender Name**: Company name or custom name
   - **Use TLS**: Check this box (recommended)
   - **Use SSL**: Leave unchecked for Gmail

### Step 3: Gmail App Password Setup
For Gmail accounts:
1. Enable 2-Factor Authentication on Gmail account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate App Password:
   - Select "Mail"
   - Select "Other (Custom name)"
   - Enter "GearGuard"
   - Copy the 16-character password
4. Paste the App Password in **SMTP Password** field

### Step 4: Save Configuration
1. Click **Save**
2. Company email status will show as "Configured" in companies list

## How It Works

### User Registration
1. User registers with email
2. System checks user's company (if assigned)
3. If company has email config, OTP sent from company email
4. If not, uses global email config or shows in console

### User Login
1. User logs in
2. If email not verified, OTP sent from user's company email
3. After successful login, notification sent from company email

### Worker Allocation
1. Admin allocates work to worker
2. Email notification sent from worker's company email
3. Worker receives email with company branding

## Email Templates
- All email templates updated to show company name
- Email headers include company name
- Footer shows company name instead of generic "GearGuard Team"

## Status Indicators
- Companies list shows email configuration status:
  - ✅ **Configured** - Company has email settings
  - ⚠️ **Not Set** - Company needs email configuration

## Benefits
1. **Branding**: Emails appear to come from company, not generic system
2. **Organization**: Each company manages its own email
3. **Security**: Company-specific email credentials
4. **Flexibility**: Different companies can use different email providers

## Troubleshooting

### Emails Not Sending
1. Check company email configuration status
2. Verify SMTP credentials are correct
3. For Gmail, ensure App Password is used (not regular password)
4. Check console/terminal for error messages

### OTP Not Received
1. Check spam/junk folder
2. Verify email address is correct
3. Check company email configuration
4. Look for OTP in console if email not configured

### Configuration Not Saving
1. Ensure all required fields are filled
2. Check SMTP server address is correct
3. Verify port number matches server type
4. For Gmail, port 587 with TLS is recommended

## Notes
- Company email configuration is optional
- System falls back to global email config if company not configured
- Multiple companies can have different email providers
- Email passwords are stored securely in database

