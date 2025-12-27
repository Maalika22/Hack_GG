"""
GearGuard - Standalone Maintenance Management System
Flask Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import event
import os
import random
import string

# Import db and models from models
from models import db, User, Department, MaintenanceCategory, MaintenanceTeam, MaintenanceEquipment, MaintenanceRequest, Company, WorkCenter, OTP

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize db with app
db.init_app(app)

# Initialize Flask-Mail
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after app initialization
from routes import *
from admin_routes import *
from user_routes import *
from worker_routes import *

def create_tables():
    """Create database tables and initial admin user"""
    with app.app_context():
        db.create_all()
        
        # Create default company if not exists
        default_company = Company.query.filter_by(name='My Company (San Francisco)').first()
        if not default_company:
            default_company = Company(
                name='My Company (San Francisco)',
                address='San Francisco, CA',
                email='info@mycompany.com'
            )
            db.session.add(default_company)
            db.session.commit()
        
        # Create admin user if not exists (no demo data)
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@gearguard.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                full_name='Administrator',
                company_id=default_company.id
            )
            db.session.add(admin)
            db.session.commit()
        
        # Generate dummy data if database is empty (only equipment count check)
        equipment_count = MaintenanceEquipment.query.count()
        request_count = MaintenanceRequest.query.count()
        
        if equipment_count == 0:
            print("Database is empty. Generating 500 IT-related dummy data records...")
            try:
                # Import here to avoid circular imports
                import generate_dummy_data
                generate_dummy_data.generate_dummy_data()
                print("[OK] Dummy data generated successfully!")
            except Exception as e:
                print(f"[WARNING] Error generating dummy data: {str(e)}")
                import traceback
                traceback.print_exc()
                app.logger.error(f"Error generating dummy data: {str(e)}")
        elif request_count == 0:
            print("Equipment exists but no requests found. Generating requests...")
            try:
                import generate_dummy_data
                generate_dummy_data.generate_requests_only()
                print("[OK] Requests generated successfully!")
            except Exception as e:
                print(f"[WARNING] Error generating requests: {str(e)}")
                app.logger.error(f"Error generating requests: {str(e)}")

def create_demo_data():
    """Create demo data for testing - called manually via admin panel"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        return
    
    # Create categories
    categories = {
        'machinery': MaintenanceCategory(name='Machinery'),
        'vehicles': MaintenanceCategory(name='Vehicles'),
        'computers': MaintenanceCategory(name='Computers & IT'),
        'electrical': MaintenanceCategory(name='Electrical Equipment')
    }
    for cat in categories.values():
        if not MaintenanceCategory.query.filter_by(name=cat.name).first():
            db.session.add(cat)
    db.session.commit()
    
    # Create teams
    teams = {
        'mechanics': MaintenanceTeam(name='Mechanics'),
        'electricians': MaintenanceTeam(name='Electricians'),
        'it_support': MaintenanceTeam(name='IT Support')
    }
    for team in teams.values():
        if not MaintenanceTeam.query.filter_by(name=team.name).first():
            team.members.append(admin)
            db.session.add(team)
    db.session.commit()
    
    # Create equipment
    equipment_data = [
        {
            'name': 'CNC Machine 01',
            'serial_number': 'CNC-2024-001',
            'purchase_date': date(2022, 1, 15),
            'warranty_information': '3 years warranty, expires in 1 year',
            'location': 'Production Floor - Bay 3',
            'category_id': categories['machinery'].id,
            'team_id': teams['mechanics'].id,
            'technician_id': admin.id
        },
        {
            'name': 'Forklift Truck 01',
            'serial_number': 'FL-2023-045',
            'purchase_date': date(2023, 1, 20),
            'warranty_information': '2 years warranty, expires in 6 months',
            'location': 'Warehouse - Loading Bay',
            'category_id': categories['vehicles'].id,
            'team_id': teams['mechanics'].id,
            'technician_id': admin.id
        },
        {
            'name': 'Server Rack 01',
            'serial_number': 'SRV-2024-012',
            'purchase_date': date(2024, 6, 1),
            'warranty_information': '5 years warranty',
            'location': 'Server Room - Rack A',
            'category_id': categories['computers'].id,
            'team_id': teams['it_support'].id,
            'technician_id': admin.id
        }
    ]
    
    for eq_data in equipment_data:
        if not MaintenanceEquipment.query.filter_by(name=eq_data['name']).first():
            equipment = MaintenanceEquipment(**eq_data)
            db.session.add(equipment)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)

