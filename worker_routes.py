"""
Worker Routes for GearGuard
Routes for workers to view and respond to allocated work
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import app
from models import db, MaintenanceRequest, User
from decorators import user_or_admin_required
from email_utils import send_work_response_email

# Worker Dashboard
@app.route('/worker/dashboard')
@login_required
@user_or_admin_required
def worker_dashboard():
    """Worker dashboard - shows allocated work"""
    # Get all requests allocated to this worker
    allocated_requests = MaintenanceRequest.query.filter_by(
        allocated_to_id=current_user.id
    ).order_by(MaintenanceRequest.created_at.desc()).all()
    
    # Group by status
    pending_requests = [r for r in allocated_requests if r.allocation_status == 'allocated']
    accepted_requests = [r for r in allocated_requests if r.allocation_status == 'accepted']
    in_progress_requests = [r for r in allocated_requests if r.allocation_status == 'in_progress']
    completed_requests = [r for r in allocated_requests if r.allocation_status == 'completed']
    
    stats = {
        'pending': len(pending_requests),
        'accepted': len(accepted_requests),
        'in_progress': len(in_progress_requests),
        'completed': len(completed_requests),
        'total': len(allocated_requests)
    }
    
    return render_template('worker/dashboard.html', 
                         stats=stats,
                         pending_requests=pending_requests,
                         accepted_requests=accepted_requests,
                         in_progress_requests=in_progress_requests,
                         completed_requests=completed_requests)

# Worker - View Allocated Requests
@app.route('/worker/requests')
@login_required
@user_or_admin_required
def worker_requests():
    """Worker view of all allocated requests"""
    requests = MaintenanceRequest.query.filter_by(
        allocated_to_id=current_user.id
    ).order_by(MaintenanceRequest.created_at.desc()).all()
    
    return render_template('worker/requests.html', requests=requests)

# Worker - View Request Detail
@app.route('/worker/requests/<int:id>')
@login_required
@user_or_admin_required
def worker_request_detail(id):
    """Worker view of request details"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    # Verify this request is allocated to current worker
    if request_obj.allocated_to_id != current_user.id:
        flash('Access denied. This request is not allocated to you.', 'error')
        return redirect(url_for('worker_dashboard'))
    
    return render_template('worker/request_detail.html', request_obj=request_obj)

# Worker - Accept/Reject Request
@app.route('/worker/requests/<int:id>/respond', methods=['POST'])
@login_required
@user_or_admin_required
def worker_respond_request(id):
    """Worker accepts or rejects allocated request"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    # Verify this request is allocated to current worker
    if request_obj.allocated_to_id != current_user.id:
        flash('Access denied. This request is not allocated to you.', 'error')
        return redirect(url_for('worker_dashboard'))
    
    response = request.form.get('response')  # accept or reject
    reason = request.form.get('reason', '')
    proposed_deadline_str = request.form.get('proposed_deadline')
    
    if response == 'accept':
        request_obj.allocation_status = 'accepted'
        request_obj.worker_response = 'accepted'
        request_obj.worker_response_at = datetime.utcnow()
        request_obj.worker_response_reason = reason
        
        # If deadline is proposed
        if proposed_deadline_str:
            try:
                proposed_deadline = datetime.strptime(proposed_deadline_str, '%Y-%m-%dT%H:%M')
                request_obj.proposed_deadline = proposed_deadline
                request_obj.deadline_status = 'pending'
                request_obj.worker_response = 'deadline_proposed'
            except:
                pass
    else:
        request_obj.allocation_status = 'rejected'
        request_obj.worker_response = 'rejected'
        request_obj.worker_response_at = datetime.utcnow()
        request_obj.worker_response_reason = reason
    
    db.session.commit()
    
    # Send email to admin
    admin_users = User.query.filter_by(is_admin=True).all()
    for admin in admin_users:
        try:
            send_work_response_email(request_obj, admin, request_obj.worker_response)
        except Exception as e:
            app.logger.error(f"Failed to send work response email: {str(e)}")
    
    flash(f'Request {response}ed successfully!', 'success')
    return redirect(url_for('worker_request_detail', id=id))

# Worker - Update Request Status
@app.route('/worker/requests/<int:id>/update-status', methods=['POST'])
@login_required
@user_or_admin_required
def worker_update_status(id):
    """Worker updates request status (start work, complete)"""
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    # Verify this request is allocated to current worker
    if request_obj.allocated_to_id != current_user.id:
        flash('Access denied. This request is not allocated to you.', 'error')
        return redirect(url_for('worker_dashboard'))
    
    new_status = request.form.get('status')
    
    if new_status == 'in_progress':
        request_obj.allocation_status = 'in_progress'
        request_obj.stage = 'in_progress'
        if not request_obj.start_date:
            request_obj.start_date = datetime.utcnow()
    elif new_status == 'completed':
        request_obj.allocation_status = 'completed'
        request_obj.stage = 'repaired'
        if not request_obj.end_date:
            request_obj.end_date = datetime.utcnow()
    
    db.session.commit()
    flash('Request status updated successfully!', 'success')
    return redirect(url_for('worker_request_detail', id=id))

