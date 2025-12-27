import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from models import db, User
from email_utils import send_otp_email, send_login_notification, create_otp

def test_email_sending():
    print("=" * 60)
    print("EMAIL SENDING TEST")
    print("=" * 60)
    
    with app.app_context():
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            print("\n[WARNING] Email credentials not configured!")
            print("\nPlease set environment variables:")
            print("  set MAIL_USERNAME=your-email@gmail.com")
            print("  set MAIL_PASSWORD=your-app-password")
            print("\nSee EMAIL_SETUP.md for detailed instructions.")
            return
        
        print(f"\nEmail Configuration:")
        print(f"  Server: {app.config.get('MAIL_SERVER')}")
        print(f"  Port: {app.config.get('MAIL_PORT')}")
        print(f"  Username: {app.config.get('MAIL_USERNAME')}")
        print(f"  TLS: {app.config.get('MAIL_USE_TLS')}")
        
        test_email = input("\nEnter email address to send test OTP: ").strip()
        if not test_email:
            print("No email provided. Exiting.")
            return
        
        print(f"\n1. Sending OTP email to {test_email}...")
        try:
            otp_code = create_otp(test_email, 'email_verification')
            send_otp_email(test_email, otp_code, 'email_verification')
            print(f"   [OK] OTP email sent! OTP Code: {otp_code}")
            print(f"   Check your inbox at {test_email}")
        except Exception as e:
            print(f"   [FAIL] Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        user = User.query.filter_by(email=test_email).first()
        if user:
            print(f"\n2. Sending login notification to {test_email}...")
            try:
                send_login_notification(user)
                print(f"   [OK] Login notification sent!")
            except Exception as e:
                print(f"   [FAIL] Error: {str(e)}")
        else:
            print(f"\n2. User not found for {test_email}, skipping login notification test")
        
        print("\n" + "=" * 60)
        print("Test complete!")
        print("=" * 60)

if __name__ == '__main__':
    test_email_sending()

