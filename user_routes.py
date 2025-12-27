
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import app
from models import (
    db, MaintenanceEquipment, MaintenanceRequest
)
from decorators import user_or_admin_required

# User Dashboard
@app.route('/user/dashboard')
@login_required
@user_or_admin_required
def user_dashboard():
    """User dashboard - shows only their requests"""
    # Users can only see requests they created or are assigned to
    user_requests = MaintenanceRequest.query.filter(
        (MaintenanceRequest.assigned_user_id == current_user.id) |
        (MaintenanceRequest.technician_id == current_user.id)
    ).order_by(MaintenanceRequest.created_at.desc()).all()
    
    stats = {
        'my_requests': len(user_requests),
        'open_requests': len([r for r in user_requests if r.stage not in ('repaired', 'scrap')]),
        'completed_requests': len([r for r in user_requests if r.stage == 'repaired']),
        'overdue_requests': len([r for r in user_requests if r.is_overdue])
    }
    
    return render_template('user/dashboard.html', stats=stats, requests=user_requests[:10])

# User - Create Request
@app.route('/user/requests/new', methods=['GET', 'POST'])
@login_required
@user_or_admin_required
def user_request_new():
    """User can create new maintenance request"""
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id')
        equipment = MaintenanceEquipment.query.get(equipment_id)
        
        if not equipment:
            flash('Equipment not found', 'error')
            return redirect(url_for('user_request_new'))
        
        request_obj = MaintenanceRequest(
            subject=request.form.get('subject'),
            request_type=request.form.get('request_type', 'corrective'),
            equipment_id=equipment_id,
            team_id=request.form.get('team_id') or equipment.team_id,
            assigned_user_id=current_user.id,  # Auto-assign to creator
            scheduled_date=datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%dT%H:%M') if request.form.get('scheduled_date') else None
        )
        
        request_obj.auto_fill_from_equipment()
        db.session.add(request_obj)
        db.session.commit()
        
        flash('Maintenance request created successfully!', 'success')
        return redirect(url_for('user_request_detail', id=request_obj.id))
    
    # Users can only see active (non-scrap) equipment
    equipment = MaintenanceEquipment.query.filter_by(scrap=False).all()
    # Get equipment_id from query parameter if provided
    equipment_id = request.args.get('equipment_id')
    selected_equipment = None
    if equipment_id:
        selected_equipment = MaintenanceEquipment.query.get(equipment_id)
    return render_template('user/request_form.html', equipment=equipment, selected_equipment=selected_equipment)

# User - View Request Details
@app.route('/user/requests/<int:id>')
@login_required
@user_or_admin_required
def user_request_detail(id):
    """User can view request details (only their own or assigned to them)"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    # Check if user has access to this request
    if not current_user.is_admin:
        if request_obj.assigned_user_id != current_user.id and request_obj.technician_id != current_user.id:
            flash('Access denied. You can only view your own requests.', 'error')
            return redirect(url_for('user_dashboard'))
    
    return render_template('user/request_detail.html', request_obj=request_obj)

# User - List My Requests
@app.route('/user/requests')
@login_required
@user_or_admin_required
def user_requests():
    """User can view their own requests with search"""
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = MaintenanceRequest.query.filter(
        (MaintenanceRequest.assigned_user_id == current_user.id) |
        (MaintenanceRequest.technician_id == current_user.id)
    )
    
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
    
    return render_template('user/requests.html', requests_by_stage=requests_by_stage, search_query=search_query)

# User - View Equipment (Read-only)
@app.route('/user/equipment')
@login_required
@user_or_admin_required
def user_equipment():
    """User can view equipment list (read-only) with search"""
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = MaintenanceEquipment.query.filter_by(scrap=False)
    
    # Apply search filter
    if search_query:
        query = query.filter(
            or_(
                MaintenanceEquipment.name.ilike(f'%{search_query}%'),
                MaintenanceEquipment.serial_number.ilike(f'%{search_query}%'),
                MaintenanceEquipment.location.ilike(f'%{search_query}%')
            )
        )
    
    equipment = query.order_by(MaintenanceEquipment.name).all()
    return render_template('user/equipment.html', equipment=equipment, search_query=search_query)

@app.route('/user/equipment/<int:id>')
@login_required
@user_or_admin_required
def user_equipment_detail(id):
    """User can view equipment details (read-only)"""
    equipment = MaintenanceEquipment.query.get_or_404(id)
    return render_template('user/equipment_detail.html', equipment=equipment)


