from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy import event

db = SQLAlchemy()
team_members = db.Table('team_members',
    db.Column('team_id', db.Integer, db.ForeignKey('maintenance_team.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    is_portal_user = db.Column(db.Boolean, default=False)  # Portal users (regular users who sign up)
    is_third_party = db.Column(db.Boolean, default=False)  # Third party users (vendors, suppliers, etc.)
    email_verified = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100))  # Job title/position
    employee_id = db.Column(db.String(50), unique=True)  # Employee ID
    hire_date = db.Column(db.Date)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', backref='employees', lazy=True)
    owned_equipment = db.relationship('MaintenanceEquipment', foreign_keys='MaintenanceEquipment.owner_id', backref='owner', lazy=True)
    assigned_requests = db.relationship('MaintenanceRequest', foreign_keys='MaintenanceRequest.assigned_user_id', backref='assigned_user', lazy=True)
    technician_requests = db.relationship('MaintenanceRequest', foreign_keys='MaintenanceRequest.technician_id', backref='technician', lazy=True)
    teams = db.relationship('MaintenanceTeam', secondary=team_members, backref='members', lazy=True)
    
    @property
    def utilization_percentage(self):
        if not self.is_worker:
            return 0
        
        active_requests = len([r for r in self.technician_requests if r.stage not in ('repaired', 'scrap')])
        max_capacity = 10
        utilization = min((active_requests / max_capacity) * 100, 100)
        return round(utilization, 1)
    
    @property
    def role(self):
        return 'admin' if self.is_admin else 'user'
    
    @property
    def is_worker(self):
        return len(self.teams) > 0 or self.position is not None
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Company(db.Model):
    """Company model"""
    __tablename__ = 'company'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    smtp_server = db.Column(db.String(200))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_use_tls = db.Column(db.Boolean, default=True)
    smtp_use_ssl = db.Column(db.Boolean, default=False)
    smtp_username = db.Column(db.String(200))
    smtp_password = db.Column(db.String(500))
    smtp_sender_name = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    equipment = db.relationship('MaintenanceEquipment', backref='company', lazy=True)
    categories = db.relationship('MaintenanceCategory', backref='company', lazy=True)
    teams = db.relationship('MaintenanceTeam', backref='company', lazy=True)
    users = db.relationship('User', backref='company', lazy=True)
    
    def has_email_config(self):
        """Check if company has email configuration"""
        return bool(self.smtp_username and self.smtp_password)
    
    def __repr__(self):
        return f'<Company {self.name}>'

class Department(db.Model):
    """Department model"""
    __tablename__ = 'department'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    
    equipment = db.relationship('MaintenanceEquipment', backref='department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'

class MaintenanceCategory(db.Model):
    """Equipment Category Model"""
    __tablename__ = 'maintenance_category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    responsible_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Responsible person
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('MaintenanceEquipment', backref='category', lazy=True)
    responsible = db.relationship('User', foreign_keys=[responsible_id], backref='responsible_categories')
    
    @property
    def equipment_count(self):
        return len(self.equipment)
    
    def __repr__(self):
        return f'<MaintenanceCategory {self.name}>'

class MaintenanceTeam(db.Model):
    """Maintenance Team Model"""
    __tablename__ = 'maintenance_team'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    equipment = db.relationship('MaintenanceEquipment', backref='team', lazy=True)
    requests = db.relationship('MaintenanceRequest', backref='team', lazy=True)
    
    @property
    def equipment_count(self):
        return len(self.equipment)
    
    @property
    def request_count(self):
        return len(self.requests)
    
    @property
    def open_request_count(self):
        return len([r for r in self.requests if r.stage not in ('repaired', 'scrap')])
    
    @property
    def member_count(self):
        """Get count of team members"""
        return len(self.members)
    
    def __repr__(self):
        return f'<MaintenanceTeam {self.name}>'

class WorkCenter(db.Model):
    """Work Center Model"""
    __tablename__ = 'work_center'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(50))  # Work Center Code
    tag = db.Column(db.String(100))  # Tag for categorization
    alternative_work_centers = db.Column(db.Text)  # Alternative work centers (comma-separated or JSON)
    cost_per_hour = db.Column(db.Numeric(10, 2), default=1.00)  # Cost per hour
    capacity_time_efficiency = db.Column(db.Numeric(5, 2), default=100.00)  # Capacity Time Efficiency percentage
    oee_target = db.Column(db.Numeric(5, 2))  # OEE (Overall Equipment Effectiveness) Target percentage
    description = db.Column(db.Text)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    equipment = db.relationship('MaintenanceEquipment', backref='work_center', lazy=True)
    requests = db.relationship('MaintenanceRequest', backref='work_center', lazy=True)
    company = db.relationship('Company', backref='work_centers', lazy=True)
    
    def __repr__(self):
        return f'<WorkCenter {self.name}>'

class MaintenanceEquipment(db.Model):
    """Equipment Model"""
    __tablename__ = 'maintenance_equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    serial_number = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    warranty_information = db.Column(db.Text)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)  # Equipment description
    assigned_date = db.Column(db.Date)  # Date equipment was assigned
    used_in_location = db.Column(db.String(200))  # Location where equipment is used
    health_percentage = db.Column(db.Integer, default=100)  # Equipment health (0-100)
    scrap_date = db.Column(db.Date)  # Date equipment was scrapped
    
    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('maintenance_category.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    work_center_id = db.Column(db.Integer, db.ForeignKey('work_center.id'))
    
    # Status
    scrap = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requests = db.relationship('MaintenanceRequest', backref='equipment', lazy=True, cascade='all, delete-orphan')
    default_technician = db.relationship('User', foreign_keys=[technician_id], backref='technician_equipment')
    
    @property
    def maintenance_count(self):
        return len(self.requests)
    
    @property
    def open_maintenance_count(self):
        return len([r for r in self.requests if r.stage not in ('repaired', 'scrap')])
    
    @property
    def is_critical(self):
        """Check if equipment health is critical (< 30%)"""
        return self.health_percentage < 30
    
    def __repr__(self):
        return f'<MaintenanceEquipment {self.name}>'

class MaintenanceRequest(db.Model):
    """Maintenance Request Model"""
    __tablename__ = 'maintenance_request'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    request_type = db.Column(db.String(20), nullable=False, default='corrective')  # corrective or preventive
    
    # Foreign Keys
    equipment_id = db.Column(db.Integer, db.ForeignKey('maintenance_equipment.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('maintenance_category.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('maintenance_team.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    maintenance_for_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Maintenance For (user)
    work_center_id = db.Column(db.Integer, db.ForeignKey('work_center.id'))  # Work Center for the request
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime)
    duration = db.Column(db.Float)  # Hours spent
    
    # Stage
    stage = db.Column(db.String(20), nullable=False, default='new')  # new, in_progress, repaired, scrap
    
    # Dates
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_overdue(self):
        """Check if request is overdue"""
        if self.scheduled_date and self.stage not in ('repaired', 'scrap'):
            return datetime.utcnow() > self.scheduled_date
        return False
    
    def auto_fill_from_equipment(self):
        """Auto-fill category, team, and technician from equipment"""
        if self.equipment:
            self.category_id = self.equipment.category_id
            self.team_id = self.equipment.team_id
            if self.equipment.technician_id:
                self.technician_id = self.equipment.technician_id
                self.assigned_user_id = self.equipment.technician_id
    
    def update_stage(self, new_stage):
        """Update stage with automatic logic"""
        if new_stage == 'in_progress' and not self.start_date:
            self.start_date = datetime.utcnow()
        elif new_stage == 'repaired' and not self.end_date:
            self.end_date = datetime.utcnow()
            # Auto-calculate duration if not set
            if not self.duration and self.start_date:
                delta = self.end_date - self.start_date
                self.duration = delta.total_seconds() / 3600.0
        
        if new_stage == 'scrap' and self.equipment:
            self.equipment.scrap = True
        
        self.stage = new_stage
    
    # Work Allocation Workflow Fields
    allocation_status = db.Column(db.String(20), default='pending')  # pending, allocated, accepted, rejected, in_progress, completed
    allocated_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Worker assigned by admin
    allocated_at = db.Column(db.DateTime)  # When admin allocated
    worker_response = db.Column(db.String(20))  # accepted, rejected, deadline_proposed
    worker_response_at = db.Column(db.DateTime)
    worker_response_reason = db.Column(db.Text)  # Reason for acceptance/rejection
    proposed_deadline = db.Column(db.DateTime)  # Deadline proposed by worker
    deadline_status = db.Column(db.String(20))  # pending, approved, rejected
    deadline_admin_response = db.Column(db.Text)  # Admin's response to deadline
    admin_instructions = db.Column(db.Text)  # Strict instructions from admin
    deadline_approved_at = db.Column(db.DateTime)
    
    # Relationships for allocation
    allocated_to = db.relationship('User', foreign_keys=[allocated_to_id], backref='allocated_requests', lazy=True)
    maintenance_for = db.relationship('User', foreign_keys=[maintenance_for_id], backref='maintenance_requests_for', lazy=True)
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.name}>'

class OTP(db.Model):
    """OTP Model for password reset and email verification"""
    __tablename__ = 'otp'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # password_reset, email_verification
    used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def __repr__(self):
        return f'<OTP {self.email} - {self.purpose}>'

# Event listeners for auto-fill
@event.listens_for(MaintenanceRequest, 'before_insert')
def receive_before_insert(mapper, connection, target):
    """Auto-fill fields when creating request"""
    target.auto_fill_from_equipment()
    # Generate request name if not set
    if not target.name or target.name == 'New':
        last_request = db.session.query(MaintenanceRequest).order_by(MaintenanceRequest.id.desc()).first()
        if last_request:
            try:
                last_num = int(last_request.name.replace('MR', ''))
                target.name = f'MR{last_num + 1:05d}'
            except:
                target.name = 'MR00001'
        else:
            target.name = 'MR00001'

@event.listens_for(MaintenanceRequest, 'before_update')
def receive_before_update(mapper, connection, target):
    """Update equipment scrap status when request moves to scrap"""
    if target.stage == 'scrap' and target.equipment:
        target.equipment.scrap = True

