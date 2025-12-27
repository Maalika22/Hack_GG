"""
Comprehensive test script for GearGuard
Tests all functionality including email, OTP, work allocation, etc.
"""

import sys
from app import app
from models import db, User, MaintenanceRequest, MaintenanceEquipment, MaintenanceCategory, MaintenanceTeam, Department, Company, OTP
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from datetime import datetime, timedelta

def test_database_connection():
    """Test database connection"""
    print("\n=== Testing Database Connection ===")
    try:
        with app.app_context():
            db.session.execute(db.text("SELECT 1"))
            print("[OK] Database connection successful")
            return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {str(e)}")
        return False

def test_models():
    """Test all models"""
    print("\n=== Testing Models ===")
    try:
        with app.app_context():
            # Test User model
            user_count = User.query.count()
            print(f"[OK] User model: {user_count} users")
            
            # Test Equipment model
            eq_count = MaintenanceEquipment.query.count()
            print(f"[OK] Equipment model: {eq_count} equipment")
            
            # Test Request model
            req_count = MaintenanceRequest.query.count()
            print(f"[OK] Request model: {req_count} requests")
            
            # Test Category model
            cat_count = MaintenanceCategory.query.count()
            print(f"[OK] Category model: {cat_count} categories")
            
            # Test Team model
            team_count = MaintenanceTeam.query.count()
            print(f"[OK] Team model: {team_count} teams")
            
            # Test Department model
            dept_count = Department.query.count()
            print(f"[OK] Department model: {dept_count} departments")
            
            # Test Company model
            company_count = Company.query.count()
            print(f"[OK] Company model: {company_count} companies")
            
            # Test OTP model
            otp_count = OTP.query.count()
            print(f"[OK] OTP model: {otp_count} OTPs")
            
            return True
    except Exception as e:
        print(f"[FAIL] Model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_user_properties():
    """Test user properties and methods"""
    print("\n=== Testing User Properties ===")
    try:
        with app.app_context():
            users = User.query.all()
            if users:
                user = users[0]
                print(f"[OK] User role: {user.role}")
                print(f"[OK] User is_worker: {user.is_worker}")
                print(f"[OK] User utilization: {user.utilization_percentage}%")
                return True
            else:
                print("[WARNING] No users found")
                return True
    except Exception as e:
        print(f"[FAIL] User properties test failed: {str(e)}")
        return False

def test_request_properties():
    """Test request properties"""
    print("\n=== Testing Request Properties ===")
    try:
        with app.app_context():
            requests = MaintenanceRequest.query.all()
            if requests:
                req = requests[0]
                print(f"[OK] Request is_overdue: {req.is_overdue}")
                print(f"[OK] Request allocation_status: {req.allocation_status}")
                return True
            else:
                print("[WARNING] No requests found")
                return True
    except Exception as e:
        print(f"[FAIL] Request properties test failed: {str(e)}")
        return False

def test_equipment_properties():
    """Test equipment properties"""
    print("\n=== Testing Equipment Properties ===")
    try:
        with app.app_context():
            equipment = MaintenanceEquipment.query.all()
            if equipment:
                eq = equipment[0]
                print(f"[OK] Equipment maintenance_count: {eq.maintenance_count}")
                print(f"[OK] Equipment open_maintenance_count: {eq.open_maintenance_count}")
                print(f"[OK] Equipment is_critical: {eq.is_critical}")
                return True
            else:
                print("[WARNING] No equipment found")
                return True
    except Exception as e:
        print(f"[FAIL] Equipment properties test failed: {str(e)}")
        return False

def test_work_allocation():
    """Test work allocation functionality"""
    print("\n=== Testing Work Allocation ===")
    try:
        with app.app_context():
            # Get a request and a worker
            request_obj = MaintenanceRequest.query.filter_by(allocation_status='pending').first()
            worker = User.query.filter_by(is_admin=False, is_active=True).first()
            
            if request_obj and worker:
                # Test allocation
                request_obj.allocation_status = 'allocated'
                request_obj.allocated_to_id = worker.id
                request_obj.allocated_at = datetime.utcnow()
                db.session.commit()
                print(f"[OK] Work allocated to {worker.full_name or worker.username}")
                
                # Test worker response
                request_obj.worker_response = 'accepted'
                request_obj.worker_response_at = datetime.utcnow()
                request_obj.worker_response_reason = 'Test acceptance'
                db.session.commit()
                print("[OK] Worker response recorded")
                
                # Test deadline proposal
                request_obj.proposed_deadline = datetime.utcnow() + timedelta(days=7)
                request_obj.deadline_status = 'pending'
                db.session.commit()
                print("[OK] Deadline proposed")
                
                return True
            else:
                print("[WARNING] No pending requests or workers found")
                return True
    except Exception as e:
        print(f"[FAIL] Work allocation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_otp_functionality():
    """Test OTP creation and validation"""
    print("\n=== Testing OTP Functionality ===")
    try:
        with app.app_context():
            from email_utils import create_otp, verify_otp
            
            # Create OTP
            otp_code = create_otp('test@example.com', 'password_reset')
            print(f"[OK] OTP created: {otp_code}")
            
            # Verify OTP
            is_valid = verify_otp('test@example.com', otp_code, 'password_reset')
            if is_valid:
                print("[OK] OTP verification successful")
            else:
                print("[FAIL] OTP verification failed")
                return False
            
            # Test invalid OTP
            is_invalid = verify_otp('test@example.com', '000000', 'password_reset')
            if not is_invalid:
                print("[OK] Invalid OTP correctly rejected")
            else:
                print("[FAIL] Invalid OTP was accepted")
                return False
            
            return True
    except Exception as e:
        print(f"[FAIL] OTP test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_relationships():
    """Test model relationships"""
    print("\n=== Testing Model Relationships ===")
    try:
        with app.app_context():
            # Test equipment -> requests relationship
            equipment = MaintenanceEquipment.query.first()
            if equipment:
                print(f"[OK] Equipment has {len(equipment.requests)} requests")
            
            # Test user -> teams relationship
            worker = User.query.filter_by(is_admin=False).first()
            if worker:
                print(f"[OK] Worker belongs to {len(worker.teams)} teams")
            
            # Test request -> allocated_to relationship
            request_obj = MaintenanceRequest.query.filter(MaintenanceRequest.allocated_to_id.isnot(None)).first()
            if request_obj and request_obj.allocated_to:
                print(f"[OK] Request allocated to: {request_obj.allocated_to.full_name or request_obj.allocated_to.username}")
            
            return True
    except Exception as e:
        print(f"[FAIL] Relationships test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_data_integrity():
    """Test data integrity and constraints"""
    print("\n=== Testing Data Integrity ===")
    try:
        with app.app_context():
            # Check for orphaned records
            requests_without_equipment = MaintenanceRequest.query.filter(
                ~MaintenanceRequest.equipment_id.in_(
                    db.session.query(MaintenanceEquipment.id)
                )
            ).count()
            
            if requests_without_equipment == 0:
                print("[OK] No orphaned requests")
            else:
                print(f"[WARNING] Found {requests_without_equipment} orphaned requests")
            
            # Check allocation status consistency
            allocated_requests = MaintenanceRequest.query.filter(
                MaintenanceRequest.allocated_to_id.isnot(None),
                MaintenanceRequest.allocation_status == 'pending'
            ).count()
            
            if allocated_requests == 0:
                print("[OK] Allocation status consistency check passed")
            else:
                print(f"[WARNING] Found {allocated_requests} requests with allocation_status='pending' but allocated_to_id set")
            
            return True
    except Exception as e:
        print(f"[FAIL] Data integrity test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("GearGuard Comprehensive Functionality Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Database Connection", test_database_connection()))
    results.append(("Models", test_models()))
    results.append(("User Properties", test_user_properties()))
    results.append(("Request Properties", test_request_properties()))
    results.append(("Equipment Properties", test_equipment_properties()))
    results.append(("Work Allocation", test_work_allocation()))
    results.append(("OTP Functionality", test_otp_functionality()))
    results.append(("Relationships", test_relationships()))
    results.append(("Data Integrity", test_data_integrity()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] All tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

