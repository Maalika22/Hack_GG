import os
from app import app

print("=" * 60)
print("EMAIL CONFIGURATION CHECK")
print("=" * 60)

with app.app_context():
    print(f"\nMAIL_SERVER: {app.config.get('MAIL_SERVER', 'Not set')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT', 'Not set')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS', 'Not set')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME', 'Not set')}")
    print(f"MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', '')) if app.config.get('MAIL_PASSWORD') else 'Not set'}")
    print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER', 'Not set')}")
    
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print("\n[WARNING] Email credentials not configured!")
        print("\nTo configure email, set these environment variables:")
        print("  set MAIL_USERNAME=your-email@gmail.com")
        print("  set MAIL_PASSWORD=your-app-password")
        print("\nFor Gmail:")
        print("  1. Enable 2-factor authentication")
        print("  2. Generate an App Password")
        print("  3. Use the App Password as MAIL_PASSWORD")
    else:
        print("\n[OK] Email configuration found!")
        print("\nTo test email sending, run the application and try registering/login.")

