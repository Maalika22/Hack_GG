"""
Email utility functions for GearGuard
Handles email sending, OTP generation, and email templates
"""

from flask import render_template
from flask_mail import Message
from app import app, mail
from models import db, OTP, User
from datetime import datetime, timedelta
import random
import string

def generate_otp(length=6):
    """Generate a random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def create_otp(email, purpose='password_reset'):
    """Create and store OTP in database"""
    # Invalidate any existing OTPs for this email and purpose
    existing_otps = OTP.query.filter_by(email=email, purpose=purpose, used=False).all()
    for otp in existing_otps:
        otp.used = True
    
    # Create new OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=app.config['OTP_EXPIRY_MINUTES'])
    
    otp = OTP(
        email=email,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at
    )
    db.session.add(otp)
    db.session.commit()
    
    return otp_code

def verify_otp(email, otp_code, purpose='password_reset'):
    """Verify OTP code"""
    otp = OTP.query.filter_by(
        email=email,
        otp_code=otp_code,
        purpose=purpose,
        used=False
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp:
        return False
    
    if not otp.is_valid():
        return False
    
    # Mark as used
    otp.used = True
    db.session.commit()
    
    return True

def send_email(subject, recipients, template, company=None, **kwargs):
    """Send email using Flask-Mail with company-specific or global configuration"""
    from flask_mail import Mail, Message
    from models import Company
    
    mail_username = None
    mail_password = None
    mail_server = 'smtp.gmail.com'
    mail_port = 587
    mail_use_tls = True
    mail_use_ssl = False
    mail_sender = None
    
    if company and company.has_email_config():
        mail_username = company.smtp_username
        mail_password = company.smtp_password
        mail_server = company.smtp_server or 'smtp.gmail.com'
        mail_port = company.smtp_port or 587
        mail_use_tls = company.smtp_use_tls if company.smtp_use_tls is not None else True
        mail_use_ssl = company.smtp_use_ssl if company.smtp_use_ssl is not None else False
        mail_sender = company.smtp_sender_name or company.smtp_username or company.email
        print(f"[EMAIL] Using company email config: {company.name} ({mail_username})")
    else:
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        mail_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = app.config.get('MAIL_PORT', 587)
        mail_use_tls = app.config.get('MAIL_USE_TLS', True)
        mail_use_ssl = app.config.get('MAIL_USE_SSL', False)
        mail_sender = app.config.get('MAIL_DEFAULT_SENDER') or mail_username
    
    if not mail_username or not mail_password:
        error_msg = "Email configuration missing. Configure company email or set MAIL_USERNAME and MAIL_PASSWORD."
        app.logger.error(error_msg)
        print(f"\n[EMAIL ERROR] {error_msg}")
        print(f"[EMAIL DEBUG] Would send to: {recipients}, Subject: {subject}")
        if company:
            print(f"[EMAIL DEBUG] Company: {company.name}, Has config: {company.has_email_config()}")
        print(f"[EMAIL DEBUG] Server: {mail_server}, Username: {mail_username}")
        print(f"\n[QUICK FIX] Configure company email in Admin → Companies, or set environment variables:")
        print(f"  $env:MAIL_USERNAME='your-email@gmail.com'")
        print(f"  $env:MAIL_PASSWORD='your-app-password'")
        raise Exception("Email configuration missing. Please configure company email or set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
    
    try:
        old_config = {
            'MAIL_SERVER': app.config.get('MAIL_SERVER'),
            'MAIL_PORT': app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            'MAIL_USE_SSL': app.config.get('MAIL_USE_SSL'),
            'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': app.config.get('MAIL_PASSWORD'),
            'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER')
        }
        
        app.config['MAIL_SERVER'] = mail_server
        app.config['MAIL_PORT'] = mail_port
        app.config['MAIL_USE_TLS'] = mail_use_tls
        app.config['MAIL_USE_SSL'] = mail_use_ssl
        app.config['MAIL_USERNAME'] = mail_username
        app.config['MAIL_PASSWORD'] = mail_password
        app.config['MAIL_DEFAULT_SENDER'] = mail_sender
        
        mail_instance = Mail(app)
        
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=render_template(template, **kwargs),
            sender=mail_sender
        )
        mail_instance.send(msg)
        
        for key, value in old_config.items():
            if value is not None:
                app.config[key] = value
        
        app.logger.info(f"Email sent successfully to {recipients} from {mail_sender}")
        print(f"[EMAIL SENT] To: {recipients}, From: {mail_sender}, Subject: {subject}")
        return True
    except Exception as e:
        app.logger.error(f"Error sending email to {recipients}: {str(e)}")
        print(f"[EMAIL ERROR] Failed to send to {recipients}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_login_notification(user):
    """Send email notification when user successfully logs in"""
    company = user.company if hasattr(user, 'company') else None
    send_email(
        subject='Successful Login - GearGuard',
        recipients=[user.email],
        template='emails/login_notification.html',
        company=company,
        user=user,
        login_time=datetime.utcnow()
    )

def send_otp_email(email, otp_code, purpose='password_reset', user=None):
    """Send OTP code via email using company's email configuration"""
    from models import User, Company
    
    company = None
    if user and hasattr(user, 'company') and user.company:
        company = user.company
    elif email:
        user_obj = User.query.filter_by(email=email).first()
        if user_obj and user_obj.company:
            company = user_obj.company
    
    if purpose == 'password_reset':
        subject = 'Password Reset OTP - GearGuard'
        template = 'emails/password_reset_otp.html'
    elif purpose == 'email_verification':
        company_name = company.name if company else 'GearGuard'
        subject = f'Email Verification OTP - {company_name}'
        template = 'emails/email_verification_otp.html'
    else:
        company_name = company.name if company else 'GearGuard'
        subject = f'Login OTP - {company_name}'
        template = 'emails/email_verification_otp.html'
    
    try:
        result = send_email(
            subject=subject,
            recipients=[email],
            template=template,
            company=company,
            otp_code=otp_code,
            expiry_minutes=app.config['OTP_EXPIRY_MINUTES'],
            company_name=company.name if company else 'GearGuard'
        )
        
        if result:
            sender_info = f" from {company.name}" if company else ""
            print(f"\n[EMAIL SENT] OTP sent to {email}{sender_info}")
            return True
        else:
            raise Exception("Email sending returned False")
            
    except Exception as e:
        error_msg = str(e)
        if "Email configuration missing" in error_msg:
            print(f"\n[OTP CODE] Since email is not configured, here is your OTP: {otp_code}")
            print(f"[OTP CODE] Enter this code: {otp_code}")
            print(f"[OTP CODE] This OTP is valid for {app.config['OTP_EXPIRY_MINUTES']} minutes")
            if company:
                print(f"[OTP CODE] Company: {company.name} - Please configure email in Admin → Companies")
            raise Exception(f"Email not configured. OTP Code: {otp_code} (displayed in console)")
        else:
            raise Exception(f"Failed to send OTP email: {error_msg}")

def send_work_allocation_email(request_obj, worker):
    """Send email to worker when work is allocated"""
    company = worker.company if hasattr(worker, 'company') and worker.company else None
    send_email(
        subject=f'New Work Allocation - {request_obj.name}',
        recipients=[worker.email],
        template='emails/work_allocation.html',
        company=company,
        request_obj=request_obj,
        worker=worker
    )

def send_work_response_email(request_obj, admin_user, response_type):
    """Send email to admin when worker responds to allocation"""
    company = admin_user.company if hasattr(admin_user, 'company') and admin_user.company else None
    send_email(
        subject=f'Work Response - {request_obj.name}',
        recipients=[admin_user.email],
        template='emails/work_response.html',
        company=company,
        request_obj=request_obj,
        admin_user=admin_user,
        response_type=response_type
    )

def send_deadline_response_email(request_obj, worker, status):
    """Send email to worker when admin responds to deadline proposal"""
    company = worker.company if hasattr(worker, 'company') and worker.company else None
    send_email(
        subject=f'Deadline Response - {request_obj.name}',
        recipients=[worker.email],
        template='emails/deadline_response.html',
        company=company,
        request_obj=request_obj,
        worker=worker,
        status=status
    )

def send_third_party_notification(third_party_user, equipment, message):
    """Send product-related information to third party users"""
    if equipment:
        subject = f'Product Update - {equipment.name}'
        template = 'emails/third_party_notification.html'
    else:
        subject = 'GearGuard - Vendor Notification'
        template = 'emails/vendor_notification.html'
    
    send_email(
        subject=subject,
        recipients=[third_party_user.email],
        template=template,
        vendor=third_party_user,
        third_party_user=third_party_user,
        equipment=equipment,
        message=message,
        admin_user=current_user if hasattr(current_user, 'is_admin') else None
    )

