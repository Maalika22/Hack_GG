
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import or_
from app import app
from models import (
    db, User, Department, MaintenanceCategory, MaintenanceTeam,
    MaintenanceEquipment, MaintenanceRequest, Company, WorkCenter
)
from werkzeug.security import generate_password_hash
from decorators import admin_required
from email_utils import send_work_allocation_email, send_work_response_email, send_deadline_response_email, send_third_party_notification

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with system overview and KPIs"""
    # Calculate Critical Equipment (health < 30%)
    all_equipment = MaintenanceEquipment.query.filter_by(scrap=False).all()
    critical_equipment = [eq for eq in all_equipment if eq.health_percentage < 30]
    critical_count = len(critical_equipment)
    
    # Calculate Technician Utilization
    technicians = User.query.filter(User.is_admin == False, User.is_active == True).all()
    total_utilization = 0
    active_technicians = 0
    for tech in technicians:
        if tech.is_worker:
            util = tech.utilization_percentage
            if util > 0:
                total_utilization += util
                active_technicians += 1
    
    avg_technician_load = round(total_utilization / active_technicians, 1) if active_technicians > 0 else 0
    
    # Get open and overdue requests
    all_requests = MaintenanceRequest.query.all()
    open_requests = [r for r in all_requests if r.stage not in ('repaired', 'scrap')]
    overdue_requests = [r for r in open_requests if r.is_overdue]
    
    stats = {
        'total_equipment': len(all_equipment),
        'total_requests': len(all_requests),
        'open_requests': len(open_requests),
        'overdue_requests': len(overdue_requests),
        'critical_equipment': critical_count,
        'technician_load': avg_technician_load,
        'total_workers': User.query.filter_by(is_admin=False, is_active=True).count(),
        'total_teams': MaintenanceTeam.query.count(),
        'total_categories': MaintenanceCategory.query.count(),
        'total_departments': Department.query.count()
    }
    
    # Activity table data (recent requests with all details)
    recent_requests = MaintenanceRequest.query.order_by(
        MaintenanceRequest.created_at.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_requests=recent_requests)

# Admin - Requests Management
@app.route('/admin/requests')
@login_required
@admin_required
def admin_requests():
    """Admin view of all requests with search"""
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = MaintenanceRequest.query
    
    # Apply search filter
    if search_query:
        query = query.join(MaintenanceEquipment).filter(
            or_(
                MaintenanceRequest.name.ilike(f'%{search_query}%'),
                MaintenanceRequest.subject.ilike(f'%{search_query}%'),
                MaintenanceRequest.request_type.ilike(f'%{search_query}%'),
                MaintenanceEquipment.name.ilike(f'%{search_query}%'),
                MaintenanceEquipment.serial_number.ilike(f'%{search_query}%')
            )
        )
    
    requests = query.order_by(MaintenanceRequest.created_at.desc()).all()
    requests_by_stage = {
        'new': [r for r in requests if r.stage == 'new'],
        'in_progress': [r for r in requests if r.stage == 'in_progress'],
        'repaired': [r for r in requests if r.stage == 'repaired'],
        'scrap': [r for r in requests if r.stage == 'scrap']
    }
    workers = User.query.filter_by(is_admin=False, is_active=True).all()
    return render_template('admin/requests.html', requests_by_stage=requests_by_stage, workers=workers, search_query=search_query)

# Admin - Equipment Management
@app.route('/admin/equipment')
@login_required
@admin_required
def admin_equipment():
    """Admin equipment management with search"""
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = MaintenanceEquipment.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            or_(
                MaintenanceEquipment.name.ilike(f'%{search_query}%'),
                MaintenanceEquipment.serial_number.ilike(f'%{search_query}%'),
                MaintenanceEquipment.location.ilike(f'%{search_query}%'),
                MaintenanceEquipment.description.ilike(f'%{search_query}%')
            )
        )
    
    equipment = query.order_by(MaintenanceEquipment.name).all()
    return render_template('equipment/list.html', equipment=equipment, search_query=search_query)

@app.route('/admin/equipment/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_equipment_new():
    """Create new equipment (admin)"""
    return redirect(url_for('equipment_new'))

@app.route('/admin/equipment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_equipment_edit(id):
    """Edit equipment (admin)"""
    return redirect(url_for('equipment_edit', id=id))

@app.route('/admin/equipment/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_equipment_delete(id):
    """Delete equipment"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    
    # Check if equipment has active requests
    active_requests = MaintenanceRequest.query.filter_by(equipment_id=id).filter(
        MaintenanceRequest.stage.in_(['new', 'in_progress'])
    ).count()
    
    if active_requests > 0:
        flash(f'Cannot delete equipment with {active_requests} active maintenance request(s). Please complete or cancel the requests first.', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    # Mark as scrap instead of deleting
    equipment.scrap = True
    db.session.commit()
    flash('Equipment marked as scrap successfully!', 'success')
    return redirect(url_for('admin_equipment'))

# Admin - Teams Management
@app.route('/admin/teams')
@login_required
@admin_required
def admin_teams():
    """Admin teams management"""
    teams = MaintenanceTeam.query.all()
    return render_template('admin/teams.html', teams=teams)

@app.route('/admin/teams/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_team_new():
    """Create or edit team (admin)"""
    return redirect(url_for('team_new'))

@app.route('/admin/teams/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_team_delete(id):
    """Delete team"""
    team = MaintenanceTeam.query.get_or_404(id)
    
    # Check if team has equipment or requests
    equipment_count = MaintenanceEquipment.query.filter_by(team_id=id).count()
    requests_count = MaintenanceRequest.query.filter_by(team_id=id).count()
    
    if equipment_count > 0 or requests_count > 0:
        flash(f'Cannot delete team. It has {equipment_count} equipment and {requests_count} requests assigned.', 'error')
        return redirect(url_for('admin_teams'))
    
    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('admin_teams'))

# Admin - Workers Management
@app.route('/admin/workers')
@login_required
@admin_required
def admin_workers():
    """Admin workers/employees management"""
    workers = User.query.filter_by(is_admin=False).order_by(User.full_name).all()
    departments = Department.query.all()
    companies = Company.query.all()
    return render_template('admin/workers.html', workers=workers, departments=departments, companies=companies)

@app.route('/admin/workers/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_worker_new():
    """Create new worker"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        position = request.form.get('position')
        employee_id = request.form.get('employee_id')
        department_id = request.form.get('department_id') or None
        hire_date_str = request.form.get('hire_date')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin_worker_new'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('admin_worker_new'))
        
        if employee_id and User.query.filter_by(employee_id=employee_id).first():
            flash('Employee ID already exists', 'error')
            return redirect(url_for('admin_worker_new'))
        
        hire_date = None
        if hire_date_str:
            try:
                hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
            except:
                pass
        
        worker = User(
            username=username.strip(),
            email=email.strip(),
            password_hash=generate_password_hash(password),
            full_name=full_name.strip() if full_name else None,
            phone=phone.strip() if phone else None,
            position=position.strip() if position else None,
            employee_id=employee_id.strip() if employee_id else None,
            department_id=department_id,
            company_id=request.form.get('company_id') or None,
            hire_date=hire_date,
            is_admin=False,
            is_portal_user=False
        )
        db.session.add(worker)
        db.session.commit()
        flash('Worker created successfully!', 'success')
        return redirect(url_for('admin_workers'))
    
    departments = Department.query.all()
    companies = Company.query.all()
    return render_template('admin/worker_form.html', departments=departments, companies=companies)

@app.route('/admin/workers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_worker_edit(id):
    """Edit worker"""
    worker = User.query.get_or_404(id)
    if worker.is_admin:
        flash('Cannot edit admin user', 'error')
        return redirect(url_for('admin_workers'))
    
    if request.method == 'POST':
        worker.email = request.form.get('email')
        worker.full_name = request.form.get('full_name')
        worker.phone = request.form.get('phone')
        worker.position = request.form.get('position')
        worker.employee_id = request.form.get('employee_id')
        worker.department_id = request.form.get('department_id') or None
        worker.company_id = request.form.get('company_id') or None
        worker.is_active = 'is_active' in request.form
        
        hire_date_str = request.form.get('hire_date')
        if hire_date_str:
            try:
                worker.hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
            except:
                pass
        
        if request.form.get('password'):
            worker.password_hash = generate_password_hash(request.form.get('password'))
        
        db.session.commit()
        flash('Worker updated successfully!', 'success')
        return redirect(url_for('admin_workers'))
    
    departments = Department.query.all()
    companies = Company.query.all()
    return render_template('admin/worker_form.html', worker=worker, departments=departments, companies=companies)

@app.route('/admin/workers/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_worker_delete(id):
    """Delete worker (soft delete)"""
    worker = User.query.get_or_404(id)
    if worker.is_admin:
        flash('Cannot delete admin user', 'error')
        return redirect(url_for('admin_workers'))
    
    worker.is_active = False
    db.session.commit()
    flash('Worker deactivated successfully', 'success')
    return redirect(url_for('admin_workers'))

# Admin - Categories Management
@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    """Admin categories management"""
    categories = MaintenanceCategory.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_category_new():
    """Create or edit category (admin)"""
    return redirect(url_for('category_new'))

@app.route('/admin/categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_category_delete(id):
    """Delete category"""
    category = MaintenanceCategory.query.get_or_404(id)
    
    # Check if category has equipment
    equipment_count = MaintenanceEquipment.query.filter_by(category_id=id).count()
    
    if equipment_count > 0:
        flash(f'Cannot delete category. It has {equipment_count} equipment assigned.', 'error')
        return redirect(url_for('admin_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_categories'))

# Admin - Company Management
@app.route('/admin/companies')
@login_required
@admin_required
def admin_companies():
    """Admin companies management"""
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

@app.route('/admin/companies/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_company_new():
    """Create new company"""
    company_id = request.args.get('id')
    company = None
    if company_id:
        company = Company.query.get_or_404(company_id)
    
    if request.method == 'POST':
        if company:
            company.name = request.form.get('name')
            company.address = request.form.get('address')
            company.phone = request.form.get('phone')
            company.email = request.form.get('email')
            company.smtp_server = request.form.get('smtp_server') or None
            company.smtp_port = int(request.form.get('smtp_port')) if request.form.get('smtp_port') else 587
            company.smtp_use_tls = 'smtp_use_tls' in request.form
            company.smtp_use_ssl = 'smtp_use_ssl' in request.form
            company.smtp_username = request.form.get('smtp_username') or None
            company.smtp_password = request.form.get('smtp_password') or None
            company.smtp_sender_name = request.form.get('smtp_sender_name') or None
        else:
            company = Company(
                name=request.form.get('name'),
                address=request.form.get('address'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                smtp_server=request.form.get('smtp_server') or None,
                smtp_port=int(request.form.get('smtp_port')) if request.form.get('smtp_port') else 587,
                smtp_use_tls='smtp_use_tls' in request.form,
                smtp_use_ssl='smtp_use_ssl' in request.form,
                smtp_username=request.form.get('smtp_username') or None,
                smtp_password=request.form.get('smtp_password') or None,
                smtp_sender_name=request.form.get('smtp_sender_name') or None
            )
            db.session.add(company)
        db.session.commit()
        flash('Company saved successfully!', 'success')
        return redirect(url_for('admin_companies'))
    
    return render_template('admin/company_form.html', company=company)

@app.route('/admin/companies/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_company_delete(id):
    """Delete company"""
    company = Company.query.get_or_404(id)
    
    users_count = User.query.filter_by(company_id=id).count()
    equipment_count = MaintenanceEquipment.query.filter_by(company_id=id).count()
    categories_count = MaintenanceCategory.query.filter_by(company_id=id).count()
    teams_count = MaintenanceTeam.query.filter_by(company_id=id).count()
    
    if users_count > 0 or equipment_count > 0 or categories_count > 0 or teams_count > 0:
        flash(f'Cannot delete company. It has {users_count} users, {equipment_count} equipment, {categories_count} categories, and {teams_count} teams assigned.', 'error')
        return redirect(url_for('admin_companies'))
    
    db.session.delete(company)
    db.session.commit()
    flash('Company deleted successfully!', 'success')
    return redirect(url_for('admin_companies'))

# Admin - Work Center Management
@app.route('/admin/work-centers')
@login_required
@admin_required
def admin_work_centers():
    """Admin work centers management"""
    work_centers = WorkCenter.query.all()
    companies = Company.query.all()
    return render_template('admin/work_centers.html', work_centers=work_centers, companies=companies)

@app.route('/admin/work-centers/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_work_center_new():
    """Create new work center"""
    work_center_id = request.args.get('id')
    work_center = None
    if work_center_id:
        work_center = WorkCenter.query.get_or_404(work_center_id)
    
    if request.method == 'POST':
        from decimal import Decimal
        if work_center:
            work_center.name = request.form.get('name')
            work_center.code = request.form.get('code') or None
            work_center.tag = request.form.get('tag') or None
            work_center.alternative_work_centers = request.form.get('alternative_work_centers') or None
            work_center.cost_per_hour = Decimal(request.form.get('cost_per_hour', '1.00')) if request.form.get('cost_per_hour') else Decimal('1.00')
            work_center.capacity_time_efficiency = Decimal(request.form.get('capacity_time_efficiency', '100.00')) if request.form.get('capacity_time_efficiency') else Decimal('100.00')
            work_center.oee_target = Decimal(request.form.get('oee_target', '0')) if request.form.get('oee_target') else None
            work_center.description = request.form.get('description') or None
            work_center.company_id = request.form.get('company_id') or None
        else:
            work_center = WorkCenter(
                name=request.form.get('name'),
                code=request.form.get('code') or None,
                tag=request.form.get('tag') or None,
                alternative_work_centers=request.form.get('alternative_work_centers') or None,
                cost_per_hour=Decimal(request.form.get('cost_per_hour', '1.00')) if request.form.get('cost_per_hour') else Decimal('1.00'),
                capacity_time_efficiency=Decimal(request.form.get('capacity_time_efficiency', '100.00')) if request.form.get('capacity_time_efficiency') else Decimal('100.00'),
                oee_target=Decimal(request.form.get('oee_target', '0')) if request.form.get('oee_target') else None,
                description=request.form.get('description') or None,
                company_id=request.form.get('company_id') or None
            )
            db.session.add(work_center)
        db.session.commit()
        flash('Work Center saved successfully!', 'success')
        return redirect(url_for('admin_work_centers'))
    
    companies = Company.query.all()
    return render_template('admin/work_center_form.html', work_center=work_center, companies=companies)

@app.route('/admin/work-centers/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_work_center_delete(id):
    """Delete work center"""
    work_center = WorkCenter.query.get_or_404(id)
    
    # Check if work center has equipment or requests
    equipment_count = MaintenanceEquipment.query.filter_by(work_center_id=id).count()
    requests_count = MaintenanceRequest.query.filter_by(work_center_id=id).count()
    
    if equipment_count > 0 or requests_count > 0:
        flash(f'Cannot delete work center. It has {equipment_count} equipment and {requests_count} requests assigned.', 'error')
        return redirect(url_for('admin_work_centers'))
    
    db.session.delete(work_center)
    db.session.commit()
    flash('Work center deleted successfully!', 'success')
    return redirect(url_for('admin_work_centers'))

# Admin - Departments Management
@app.route('/admin/departments')
@login_required
@admin_required
def admin_departments():
    """Admin departments management"""
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/departments/new', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_department_new():
    """Create new department"""
    if request.method == 'POST':
        department = Department(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(department)
        db.session.commit()
        flash('Department created successfully!', 'success')
        return redirect(url_for('admin_departments'))
    
    return render_template('admin/department_form.html')

@app.route('/admin/departments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_department_edit(id):
    """Edit department"""
    department = Department.query.get_or_404(id)
    
    if request.method == 'POST':
        department.name = request.form.get('name')
        department.description = request.form.get('description')
        db.session.commit()
        flash('Department updated successfully!', 'success')
        return redirect(url_for('admin_departments'))
    
    return render_template('admin/department_form.html', department=department)

@app.route('/admin/departments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_department_delete(id):
    """Delete department"""
    department = Department.query.get_or_404(id)
    
    # Check if department has users or equipment
    users_count = User.query.filter_by(department_id=id).count()
    equipment_count = MaintenanceEquipment.query.filter_by(department_id=id).count()
    
    if users_count > 0 or equipment_count > 0:
        flash(f'Cannot delete department. It has {users_count} users and {equipment_count} equipment assigned.', 'error')
        return redirect(url_for('admin_departments'))
    
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('admin_departments'))

# Admin - Work Allocation
@app.route('/admin/requests/<int:id>/allocate', methods=['POST'])
@login_required
@admin_required
def admin_allocate_request(id):
    """Allocate work request to a worker"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    worker_id = request.form.get('worker_id')
    
    if not worker_id:
        flash('Please select a worker', 'error')
        return redirect(url_for('admin_requests'))
    
    worker = User.query.get(worker_id)
    if not worker or worker.is_admin:
        flash('Invalid worker selected', 'error')
        return redirect(url_for('admin_requests'))
    
    # Allocate request
    request_obj.allocation_status = 'allocated'
    request_obj.allocated_to_id = worker_id
    request_obj.allocated_at = datetime.utcnow()
    request_obj.technician_id = worker_id
    request_obj.assigned_user_id = worker_id
    
    db.session.commit()
    
    # Send email notification
    try:
        send_work_allocation_email(request_obj, worker)
    except Exception as e:
        app.logger.error(f"Failed to send allocation email: {str(e)}")
    
    flash(f'Work allocated to {worker.full_name or worker.username} successfully!', 'success')
    return redirect(url_for('admin_requests'))

@app.route('/admin/requests/<int:id>/deadline-response', methods=['POST'])
@login_required
@admin_required
def admin_deadline_response(id):
    """Admin responds to worker's deadline proposal"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    response = request.form.get('response')  # approve or reject
    admin_response = request.form.get('admin_response', '')
    admin_instructions = request.form.get('admin_instructions', '')
    
    if response == 'approve':
        request_obj.deadline_status = 'approved'
        request_obj.deadline_approved_at = datetime.utcnow()
        if admin_instructions:
            request_obj.admin_instructions = admin_instructions
    else:
        request_obj.deadline_status = 'rejected'
        request_obj.deadline_admin_response = admin_response
    
    db.session.commit()
    
    # Send email to worker
    worker = request_obj.allocated_to
    if worker:
        try:
            send_deadline_response_email(request_obj, worker, response)
        except Exception as e:
            app.logger.error(f"Failed to send deadline response email: {str(e)}")
    
    flash(f'Deadline {response}d successfully!', 'success')
    return redirect(url_for('admin_requests'))

@app.route('/admin/vendors')
@login_required
@admin_required
def admin_vendors():
    """Admin view of all third-party vendors"""
    vendors = User.query.filter_by(is_third_party=True, is_active=True).all()
    return render_template('admin/vendors.html', vendors=vendors)

@app.route('/admin/vendors/send-email', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_send_vendor_email():
    """Admin can send email to vendors"""
    vendors = User.query.filter_by(is_third_party=True, is_active=True).all()
    
    if request.method == 'POST':
        vendor_ids = request.form.getlist('vendor_ids')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        
        if not vendor_ids:
            flash('Please select at least one vendor', 'error')
            return render_template('admin/vendor_email.html', vendors=vendors)
        
        if not subject or not message:
            flash('Subject and message are required', 'error')
            return render_template('admin/vendor_email.html', vendors=vendors)
        
        notified_count = 0
        for vendor_id in vendor_ids:
            vendor = User.query.get(vendor_id)
            if vendor and vendor.is_third_party:
                try:
                    # Use custom subject from form
                    from email_utils import send_email
                    send_email(
                        subject=subject,
                        recipients=[vendor.email],
                        template='emails/vendor_notification.html',
                        vendor=vendor,
                        third_party_user=vendor,
                        equipment=None,
                        message=message,
                        admin_user=current_user
                    )
                    notified_count += 1
                except Exception as e:
                    app.logger.error(f"Failed to send email to vendor {vendor.email}: {str(e)}")
        
        flash(f'Email sent to {notified_count} vendor(s)!', 'success')
        return redirect(url_for('admin_vendors'))
    
    return render_template('admin/vendor_email.html', vendors=vendors)

@app.route('/admin/equipment/<int:id>/notify-third-party', methods=['POST'])
@login_required
@admin_required
def admin_notify_third_party(id):
    """Send product-related information to third party users"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    third_party_ids = request.form.getlist('third_party_ids')
    message = request.form.get('message', '')
    
    if not third_party_ids:
        flash('Please select at least one third party user', 'error')
        return redirect(url_for('equipment_detail', id=id))
    
    notified_count = 0
    for tp_id in third_party_ids:
        third_party = User.query.get(tp_id)
        if third_party and third_party.is_third_party:
            try:
                send_third_party_notification(third_party, equipment, message)
                notified_count += 1
            except Exception as e:
                app.logger.error(f"Failed to notify third party {third_party.email}: {str(e)}")
    
    flash(f'Notification sent to {notified_count} third party user(s)!', 'success')
    return redirect(url_for('equipment_detail', id=id))

# Note: Index route is in routes.py

