"""
Flask Routes for GearGuard
All application routes and views
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from app import app
from models import (
    db, User, Department, MaintenanceCategory, MaintenanceTeam,
    MaintenanceEquipment, MaintenanceRequest, Company, WorkCenter, OTP
)
from decorators import admin_required
from email_utils import (
    send_login_notification, send_otp_email, verify_otp, create_otp,
    send_work_allocation_email, send_work_response_email, send_deadline_response_email
)

# Authentication Routes
@app.route('/')
def index():
    """Home page - redirect based on role"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with email - redirects based on role"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Account is deactivated. Please contact administrator.', 'error')
                return render_template('login.html')
            
            if not user.email_verified and not user.is_admin:
                session['verify_email'] = email
                otp_code = create_otp(email, 'email_verification')
                try:
                    send_otp_email(email, otp_code, 'email_verification', user=user)
                    company_name = user.company.name if user.company else 'GearGuard'
                    flash(f'Please verify your email before logging in. OTP has been sent to your email from {company_name}.', 'warning')
                    app.logger.info(f"OTP sent to {email} for email verification from company: {company_name}")
                except Exception as e:
                    error_msg = str(e)
                    app.logger.error(f"Failed to send verification OTP to {email}: {error_msg}")
                    if "OTP Code:" in error_msg:
                        otp_display = error_msg.split("OTP Code:")[1].strip()
                        flash(f'Email not configured. OTP Code: {otp_display} (check console). Please verify your email.', 'warning')
                    else:
                        flash(f'Failed to send verification email: {error_msg}. Please check email configuration.', 'error')
                    return render_template('login.html')
                return redirect(url_for('verify_email'))
            
            login_user(user)
            flash('Logged in successfully!', 'success')
            
            try:
                send_login_notification(user)
                company_name = user.company.name if user.company else 'GearGuard'
                app.logger.info(f"Login notification sent to {user.email} from {company_name}")
            except Exception as e:
                app.logger.error(f"Failed to send login notification to {user.email}: {str(e)}")
                flash(f'Login successful, but failed to send notification email: {str(e)}', 'warning')
            
            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            if not user:
                flash('Account does not exist', 'error')
            else:
                flash('Invalid password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - send OTP via email"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found in our system.', 'error')
            return render_template('forgot_password.html')
        
        otp_code = create_otp(email, 'password_reset')
        session['reset_email'] = email
        try:
            send_otp_email(email, otp_code, 'password_reset', user=user)
            company_name = user.company.name if user.company else 'GearGuard'
            flash(f'OTP has been sent to your email from {company_name}. Please check your inbox.', 'success')
            app.logger.info(f"Password reset OTP sent to {email} from {company_name}")
        except Exception as e:
            error_msg = str(e)
            app.logger.error(f"Failed to send password reset OTP to {email}: {error_msg}")
            if "OTP Code:" in error_msg:
                otp_display = error_msg.split("OTP Code:")[1].strip()
                flash(f'Email not configured. OTP Code: {otp_display} (check console).', 'warning')
            else:
                flash(f'Failed to send OTP email: {error_msg}. Please check email configuration.', 'error')
            return render_template('forgot_password.html')
        return redirect(url_for('reset_password'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password using OTP"""
    email = session.get('reset_email')
    if not email:
        flash('Please request password reset first.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify OTP
        if not verify_otp(email, otp_code, 'password_reset'):
            flash('Invalid or expired OTP. Please try again.', 'error')
            return render_template('reset_password.html', email=email)
        
        # Validate password
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', email=email)
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('reset_password.html', email=email)
        
        # Update password
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            session.pop('reset_email', None)
            flash('Password reset successfully! Please login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', email=email)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.phone = request.form.get('phone')
        current_user.position = request.form.get('position')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('profile.html')
            current_user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Portal user registration with password validation"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        re_enter_password = request.form.get('re_enter_password')
        
        # Validation
        errors = []
        if not name or len(name.strip()) < 2:
            errors.append('Name must be at least 2 characters long')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address')
        
        # Password validation: uppercase, lowercase, special char, 8+ characters
        if not password:
            errors.append('Password is required')
        else:
            if len(password) < 8:
                errors.append('Password must be at least 8 characters long')
            if not any(c.isupper() for c in password):
                errors.append('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in password):
                errors.append('Password must contain at least one lowercase letter')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
                errors.append('Password must contain at least one special character')
        
        if password != re_enter_password:
            errors.append('Passwords do not match')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already exists in database')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html', name=name, email=email)
        
        # Generate username from email
        username = email.split('@')[0]
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            username=username,
            email=email.strip(),
            password_hash=generate_password_hash(password),
            full_name=name.strip(),
            is_portal_user=True,
            is_admin=False,
            email_verified=False
        )
        db.session.add(user)
        db.session.commit()
        
        otp_code = create_otp(email, 'email_verification')
        session['verify_email'] = email
        user_obj = User.query.filter_by(email=email).first()
        try:
            send_otp_email(email, otp_code, 'email_verification', user=user_obj)
            company_name = user_obj.company.name if user_obj and user_obj.company else 'GearGuard'
            flash(f'Registration successful! Please verify your email with the OTP sent to your inbox from {company_name}.', 'success')
            app.logger.info(f"OTP sent to {email} for email verification after registration from {company_name}")
        except Exception as e:
            error_msg = str(e)
            app.logger.error(f"Failed to send verification OTP to {email}: {error_msg}")
            if "OTP Code:" in error_msg:
                otp_display = error_msg.split("OTP Code:")[1].strip()
                flash(f'Registration successful! Email not configured. OTP Code: {otp_display} (check console for details)', 'warning')
            else:
                flash(f'Registration successful, but failed to send verification email: {error_msg}. Please check email configuration.', 'warning')
        return redirect(url_for('verify_email'))
    
    return render_template('register.html')

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Email verification with OTP"""
    email = session.get('verify_email')
    if not email:
        flash('Please register first.', 'error')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        
        if not verify_otp(email, otp_code, 'email_verification'):
            flash('Invalid or expired OTP. Please try again.', 'error')
            return render_template('verify_email.html', email=email)
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_verified = True
            db.session.commit()
            flash('Email verified successfully! You can now login.', 'success')
            session.pop('verify_email', None)
            return redirect(url_for('login'))
        else:
            flash('User not found. Please register again.', 'error')
            session.pop('verify_email', None)
            return redirect(url_for('register'))
    
    return render_template('verify_email.html', email=email)

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for email verification"""
    email = session.get('verify_email')
    if not email:
        flash('Please register first.', 'error')
        return redirect(url_for('register'))
    
    user_obj = User.query.filter_by(email=email).first()
    otp_code = create_otp(email, 'email_verification')
    try:
        send_otp_email(email, otp_code, 'email_verification', user=user_obj)
        company_name = user_obj.company.name if user_obj and user_obj.company else 'GearGuard'
        flash(f'OTP has been resent to your email from {company_name}.', 'success')
        app.logger.info(f"OTP resent to {email} from {company_name}")
    except Exception as e:
        error_msg = str(e)
        app.logger.error(f"Failed to resend OTP to {email}: {error_msg}")
        if "OTP Code:" in error_msg:
            otp_display = error_msg.split("OTP Code:")[1].strip()
            flash(f'Email not configured. OTP Code: {otp_display} (check console).', 'warning')
        else:
            flash(f'Failed to resend OTP: {error_msg}. Please check email configuration.', 'error')
    
    return redirect(url_for('verify_email'))

# Dashboard - redirects based on role
@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - redirects based on user role"""
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

# Equipment Routes
@app.route('/equipment')
@login_required
def equipment_list():
    """List all equipment - redirects based on role"""
    if current_user.is_admin:
        return redirect(url_for('admin_equipment'))
    else:
        return redirect(url_for('user_equipment'))

@app.route('/equipment/<int:id>')
@login_required
def equipment_detail(id):
    """Equipment detail view - redirects based on role"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    if current_user.is_admin:
        return render_template('equipment/detail.html', equipment=equipment)
    else:
        return redirect(url_for('user_equipment_detail', id=id))

@app.route('/equipment/new', methods=['GET', 'POST'])
@login_required
@admin_required
def equipment_new():
    """Create new equipment"""
    if request.method == 'POST':
        # Parse dates
        purchase_date = None
        assigned_date = None
        scrap_date = None
        if request.form.get('purchase_date'):
            purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date()
        if request.form.get('assigned_date'):
            assigned_date = datetime.strptime(request.form.get('assigned_date'), '%Y-%m-%d').date()
        if request.form.get('scrap_date'):
            scrap_date = datetime.strptime(request.form.get('scrap_date'), '%Y-%m-%d').date()
        
        equipment = MaintenanceEquipment(
            name=request.form.get('name'),
            serial_number=request.form.get('serial_number'),
            purchase_date=purchase_date,
            warranty_information=request.form.get('warranty_information'),
            location=request.form.get('location'),
            description=request.form.get('description'),
            assigned_date=assigned_date,
            used_in_location=request.form.get('used_in_location'),
            health_percentage=int(request.form.get('health_percentage', 100)),
            scrap_date=scrap_date,
            owner_id=request.form.get('owner_id') or None,
            department_id=request.form.get('department_id') or None,
            team_id=request.form.get('team_id'),
            technician_id=request.form.get('technician_id') or None,
            category_id=request.form.get('category_id') or None,
            company_id=request.form.get('company_id') or None,
            work_center_id=request.form.get('work_center_id') or None,
            scrap='scrap' in request.form
        )
        db.session.add(equipment)
        db.session.commit()
        flash('Equipment created successfully!', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))
    
    categories = MaintenanceCategory.query.all()
    teams = MaintenanceTeam.query.all()
    users = User.query.filter_by(is_active=True).all()
    departments = Department.query.all()
    companies = Company.query.all()
    work_centers = WorkCenter.query.all()
    
    return render_template('equipment/form.html', 
                         categories=categories, teams=teams, 
                         users=users, departments=departments,
                         companies=companies, work_centers=work_centers)

@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def equipment_edit(id):
    """Edit equipment"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    
    if request.method == 'POST':
        equipment.name = request.form.get('name')
        equipment.serial_number = request.form.get('serial_number')
        if request.form.get('purchase_date'):
            equipment.purchase_date = datetime.strptime(request.form.get('purchase_date'), '%Y-%m-%d').date()
        if request.form.get('assigned_date'):
            equipment.assigned_date = datetime.strptime(request.form.get('assigned_date'), '%Y-%m-%d').date()
        if request.form.get('scrap_date'):
            equipment.scrap_date = datetime.strptime(request.form.get('scrap_date'), '%Y-%m-%d').date()
        equipment.warranty_information = request.form.get('warranty_information')
        equipment.location = request.form.get('location')
        equipment.description = request.form.get('description')
        equipment.used_in_location = request.form.get('used_in_location')
        equipment.health_percentage = int(request.form.get('health_percentage', 100))
        equipment.owner_id = request.form.get('owner_id') or None
        equipment.department_id = request.form.get('department_id') or None
        equipment.team_id = request.form.get('team_id')
        equipment.technician_id = request.form.get('technician_id') or None
        equipment.category_id = request.form.get('category_id') or None
        equipment.company_id = request.form.get('company_id') or None
        equipment.work_center_id = request.form.get('work_center_id') or None
        equipment.scrap = 'scrap' in request.form
        
        db.session.commit()
        flash('Equipment updated successfully!', 'success')
        return redirect(url_for('equipment_detail', id=equipment.id))
    
    categories = MaintenanceCategory.query.all()
    teams = MaintenanceTeam.query.all()
    users = User.query.filter_by(is_active=True).all()
    departments = Department.query.all()
    companies = Company.query.all()
    work_centers = WorkCenter.query.all()
    
    return render_template('equipment/form.html', equipment=equipment,
                         categories=categories, teams=teams, 
                         users=users, departments=departments,
                         companies=companies, work_centers=work_centers)

# Maintenance Request Routes
@app.route('/requests')
@login_required
def request_list():
    """List all maintenance requests - redirects based on role"""
    if current_user.is_admin:
        return redirect(url_for('admin_requests'))
    else:
        return redirect(url_for('user_requests'))

@app.route('/requests/calendar')
@login_required
def request_calendar():
    """Calendar view for preventive maintenance"""
    # Show all requests with scheduled dates, but highlight preventive ones
    requests = MaintenanceRequest.query.filter(
        MaintenanceRequest.scheduled_date.isnot(None)
    ).all()
    return render_template('requests/calendar.html', requests=requests)

@app.route('/requests/<int:id>')
@login_required
def request_detail(id):
    """Request detail view - redirects based on role"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    if current_user.is_admin:
        return render_template('requests/detail.html', request_obj=request_obj)
    else:
        # Check if user has access
        if request_obj.assigned_user_id != current_user.id and request_obj.technician_id != current_user.id:
            flash('Access denied. You can only view your own requests.', 'error')
            return redirect(url_for('user_dashboard'))
        return redirect(url_for('user_request_detail', id=id))

@app.route('/requests/new', methods=['GET', 'POST'])
@login_required
@admin_required
def request_new():
    """Create new maintenance request"""
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id')
        equipment = MaintenanceEquipment.query.get(equipment_id)
        
        if not equipment:
            flash('Equipment not found', 'error')
            return redirect(url_for('request_new'))
        
        request_obj = MaintenanceRequest(
            subject=request.form.get('subject'),
            request_type=request.form.get('request_type', 'corrective'),
            equipment_id=equipment_id,
            team_id=request.form.get('team_id') or equipment.team_id,
            assigned_user_id=request.form.get('assigned_user_id') or current_user.id,
            maintenance_for_id=request.form.get('maintenance_for_id') or None,
            work_center_id=request.form.get('work_center_id') or equipment.work_center_id,
            scheduled_date=datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%dT%H:%M') if request.form.get('scheduled_date') else None
        )
        
        request_obj.auto_fill_from_equipment()
        db.session.add(request_obj)
        db.session.commit()
        
        flash('Maintenance request created successfully!', 'success')
        return redirect(url_for('request_detail', id=request_obj.id))
    
    equipment = MaintenanceEquipment.query.filter_by(scrap=False).all()
    teams = MaintenanceTeam.query.all()
    users = User.query.all()
    work_centers = WorkCenter.query.all()
    
    return render_template('requests/form.html', equipment=equipment, teams=teams, users=users, work_centers=work_centers)

@app.route('/requests/<int:id>/update_stage', methods=['POST'])
@login_required
@admin_required
def request_update_stage(id):
    """Update request stage"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    new_stage = request.form.get('stage')
    
    if new_stage in ['new', 'in_progress', 'repaired', 'scrap']:
        request_obj.update_stage(new_stage)
        db.session.commit()
        flash(f'Request moved to {new_stage.replace("_", " ").title()}', 'success')
    
    return redirect(url_for('request_detail', id=id))

@app.route('/requests/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def request_edit(id):
    """Edit maintenance request"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    if request.method == 'POST':
        request_obj.subject = request.form.get('subject')
        request_obj.request_type = request.form.get('request_type')
        request_obj.equipment_id = request.form.get('equipment_id')
        request_obj.team_id = request.form.get('team_id')
        request_obj.assigned_user_id = request.form.get('assigned_user_id')
        request_obj.technician_id = request.form.get('technician_id')
        request_obj.maintenance_for_id = request.form.get('maintenance_for_id') or None
        request_obj.work_center_id = request.form.get('work_center_id') or None
        if request.form.get('scheduled_date'):
            request_obj.scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%dT%H:%M')
        request_obj.duration = float(request.form.get('duration')) if request.form.get('duration') else None
        
        db.session.commit()
        flash('Request updated successfully!', 'success')
        return redirect(url_for('request_detail', id=request_obj.id))
    
    equipment = MaintenanceEquipment.query.all()
    teams = MaintenanceTeam.query.all()
    users = User.query.all()
    work_centers = WorkCenter.query.all()
    
    return render_template('requests/form.html', request_obj=request_obj,
                         equipment=equipment, teams=teams, users=users, work_centers=work_centers)

@app.route('/requests/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def request_delete(id):
    """Delete maintenance request"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    # Only allow deletion of new or scrap requests
    if request_obj.stage not in ['new', 'scrap']:
        flash('Cannot delete request that is in progress or repaired. Please mark as scrap first.', 'error')
        return redirect(url_for('request_detail', id=id))
    
    db.session.delete(request_obj)
    db.session.commit()
    flash('Request deleted successfully!', 'success')
    return redirect(url_for('admin_requests'))

# Team Routes
@app.route('/teams')
@login_required
def team_list():
    """List all teams - redirects to admin for admins"""
    if current_user.is_admin:
        return redirect(url_for('admin_teams'))
    else:
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('user_dashboard'))

@app.route('/teams/<int:id>')
@login_required
def team_detail(id):
    """Team detail view"""
    team = MaintenanceTeam.query.get_or_404(id)
    return render_template('teams/detail.html', team=team)

@app.route('/teams/new', methods=['GET', 'POST'])
@login_required
@admin_required
def team_new():
    """Create or edit team"""
    team_id = request.args.get('id')
    team = None
    if team_id:
        team = MaintenanceTeam.query.get_or_404(team_id)
    
    if request.method == 'POST':
        if team:
            team.name = request.form.get('name')
            team.company_id = request.form.get('company_id') or None
            # Update members
            team.members.clear()
            member_ids = request.form.getlist('member_ids')
            for member_id in member_ids:
                user = User.query.get(member_id)
                if user:
                    team.members.append(user)
        else:
            team = MaintenanceTeam(
                name=request.form.get('name'),
                company_id=request.form.get('company_id') or None
            )
            member_ids = request.form.getlist('member_ids')
            for member_id in member_ids:
                user = User.query.get(member_id)
                if user:
                    team.members.append(user)
            db.session.add(team)
        db.session.commit()
        flash('Team saved successfully!', 'success')
        return redirect(url_for('team_detail', id=team.id))
    
    users = User.query.filter_by(is_active=True).all()
    companies = Company.query.all()
    return render_template('teams/form.html', team=team, users=users, companies=companies)

# Category Routes
@app.route('/categories')
@login_required
def category_list():
    """List all categories - redirects to admin for admins"""
    if current_user.is_admin:
        return redirect(url_for('admin_categories'))
    else:
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('user_dashboard'))

@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def category_new():
    """Create or edit category"""
    category_id = request.args.get('id')
    category = None
    if category_id:
        category = MaintenanceCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        if category:
            category.name = request.form.get('name')
            category.responsible_id = request.form.get('responsible_id') or None
            category.company_id = request.form.get('company_id') or None
        else:
            category = MaintenanceCategory(
                name=request.form.get('name'),
                responsible_id=request.form.get('responsible_id') or None,
                company_id=request.form.get('company_id') or None
            )
            db.session.add(category)
        db.session.commit()
        flash('Category saved successfully!', 'success')
        return redirect(url_for('category_list'))
    
    users = User.query.filter_by(is_active=True).all()
    companies = Company.query.all()
    return render_template('categories/form.html', category=category, users=users, companies=companies)

# API Routes for AJAX
@app.route('/api/equipment/<int:id>/requests')
@login_required
def api_equipment_requests(id):
    """Get requests for equipment (for smart button)"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    requests = [{
        'id': r.id,
        'name': r.name,
        'subject': r.subject,
        'stage': r.stage
    } for r in equipment.requests]
    return jsonify(requests)

@app.route('/api/equipment/<int:id>')
@login_required
def api_equipment_detail(id):
    """Get equipment details for auto-fill"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    return jsonify({
        'category_id': equipment.category_id,
        'team_id': equipment.team_id,
        'technician_id': equipment.technician_id
    })

# Admin Routes
@app.route('/admin/clear-demo-data', methods=['POST'])
@login_required
def clear_demo_data():
    """Clear demo data (equipment, requests) but keep users"""
    if not current_user.is_admin:
        flash('Only administrators can perform this action', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Delete demo equipment
        demo_equipment = MaintenanceEquipment.query.filter(
            MaintenanceEquipment.name.in_(['CNC Machine 01', 'Forklift Truck 01', 'Server Rack 01', 'Laptop - John Doe', 'Main Transformer'])
        ).all()
        for eq in demo_equipment:
            db.session.delete(eq)
        
        # Delete demo requests
        demo_requests = MaintenanceRequest.query.filter(
            MaintenanceRequest.name.in_(['MR00001', 'MR00002', 'MR00003', 'MR00004', 'MR00005', 'MR00006'])
        ).all()
        for req in demo_requests:
            db.session.delete(req)
        
        # Delete demo categories (only if no equipment uses them)
        demo_categories = MaintenanceCategory.query.filter(
            MaintenanceCategory.name.in_(['Machinery', 'Vehicles', 'Computers & IT', 'Electrical Equipment'])
        ).all()
        for cat in demo_categories:
            if len(cat.equipment) == 0:
                db.session.delete(cat)
        
        # Delete demo teams (only if no equipment uses them)
        demo_teams = MaintenanceTeam.query.filter(
            MaintenanceTeam.name.in_(['Mechanics', 'Electricians', 'IT Support'])
        ).all()
        for team in demo_teams:
            if len(team.equipment) == 0 and len(team.requests) == 0:
                db.session.delete(team)
        
        db.session.commit()
        flash('Demo data cleared successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing demo data: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/admin/create-demo-data', methods=['POST'])
@login_required
def create_demo_data_route():
    """Create demo data for testing"""
    if not current_user.is_admin:
        flash('Only administrators can perform this action', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        from app import create_demo_data
        create_demo_data()
        flash('Demo data created successfully', 'success')
    except Exception as e:
        flash(f'Error creating demo data: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

