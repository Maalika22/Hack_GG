"""
Merge Work Centers with existing data
Assigns work centers to equipment and requests that don't have them
Preserves all existing data and functionality
"""

from app import app
from models import db, WorkCenter, MaintenanceEquipment, MaintenanceRequest, Company
import random

def merge_work_centers_with_existing_data():
    """Merge work centers with existing equipment and requests"""
    print("=" * 60)
    print("MERGING WORK CENTERS WITH EXISTING DATA")
    print("=" * 60)
    
    with app.app_context():
        # Get all work centers
        work_centers = WorkCenter.query.all()
        
        if not work_centers:
            print("[INFO] No work centers found. Creating default work centers...")
            # Create default work centers if none exist
            main_company = Company.query.first()
            if not main_company:
                main_company = Company(
                    name="TechCorp IT Solutions",
                    address="123 Tech Street, San Francisco, CA 94105",
                    phone="+1-555-0100",
                    email="info@techcorp.com"
                )
                db.session.add(main_company)
                db.session.commit()
            
            # Create work centers from the WORK_CENTERS list
            WORK_CENTERS = [
                "Assembly 1", "Assembly 2", "Drill 1", "Drill 2", "Welding Station 1",
                "Welding Station 2", "CNC Machine 1", "CNC Machine 2", "Lathe 1", "Lathe 2",
                "Milling Machine 1", "Milling Machine 2", "Testing Station 1", "Testing Station 2",
                "Quality Control 1", "Quality Control 2", "Packaging Line 1", "Packaging Line 2",
                "Inspection Bay 1", "Inspection Bay 2", "Repair Station 1", "Repair Station 2",
                "Calibration Lab", "Maintenance Bay 1", "Maintenance Bay 2"
            ]
            from decimal import Decimal
            
            for i, wc_name in enumerate(WORK_CENTERS, 1):
                wc = WorkCenter(
                    name=wc_name,
                    code=f"WC{i:03d}",
                    tag=random.choice(["Production", "Assembly", "Testing", "Quality", "Maintenance", "Repair"]),
                    alternative_work_centers=random.choice([None, f"WC{(i+1)%len(WORK_CENTERS)+1:03d}", f"WC{(i+2)%len(WORK_CENTERS)+1:03d}"]),
                    cost_per_hour=Decimal(str(random.uniform(1.00, 50.00))).quantize(Decimal('0.01')),
                    capacity_time_efficiency=Decimal(str(random.uniform(80.00, 100.00))).quantize(Decimal('0.01')),
                    oee_target=Decimal(str(random.uniform(30.00, 95.00))).quantize(Decimal('0.01')),
                    description=f"{wc_name} work center for {random.choice(['Production', 'Assembly', 'Testing', 'Maintenance'])} operations",
                    company_id=main_company.id
                )
                db.session.add(wc)
            db.session.commit()
            work_centers = WorkCenter.query.all()
            print(f"[OK] Created {len(work_centers)} work centers")
        
        print(f"[INFO] Found {len(work_centers)} work centers")
        
        # Update equipment without work centers
        equipment_without_wc = MaintenanceEquipment.query.filter_by(work_center_id=None).all()
        if equipment_without_wc:
            print(f"\n[INFO] Assigning work centers to {len(equipment_without_wc)} equipment...")
            updated_count = 0
            for eq in equipment_without_wc:
                if work_centers:
                    # Assign random work center
                    eq.work_center_id = random.choice(work_centers).id
                    updated_count += 1
            db.session.commit()
            print(f"[OK] Assigned work centers to {updated_count} equipment")
        else:
            print("[OK] All equipment already has work centers assigned")
        
        # Update requests without work centers
        requests_without_wc = MaintenanceRequest.query.filter_by(work_center_id=None).all()
        if requests_without_wc:
            print(f"\n[INFO] Assigning work centers to {len(requests_without_wc)} requests...")
            updated_count = 0
            for req in requests_without_wc:
                # Try to get work center from equipment first
                if req.equipment and req.equipment.work_center_id:
                    req.work_center_id = req.equipment.work_center_id
                elif work_centers:
                    # Assign random work center
                    req.work_center_id = random.choice(work_centers).id
                updated_count += 1
            db.session.commit()
            print(f"[OK] Assigned work centers to {updated_count} requests")
        else:
            print("[OK] All requests already have work centers assigned")
        
        # Ensure requests have work centers from their equipment if equipment has one
        requests_to_update = MaintenanceRequest.query.filter(
            MaintenanceRequest.work_center_id.is_(None),
            MaintenanceRequest.equipment_id.isnot(None)
        ).all()
        
        if requests_to_update:
            print(f"\n[INFO] Syncing work centers from equipment to {len(requests_to_update)} requests...")
            updated_count = 0
            for req in requests_to_update:
                if req.equipment and req.equipment.work_center_id:
                    req.work_center_id = req.equipment.work_center_id
                    updated_count += 1
            db.session.commit()
            print(f"[OK] Synced work centers to {updated_count} requests from their equipment")
        
        # Final statistics
        print("\n" + "=" * 60)
        print("FINAL STATISTICS")
        print("=" * 60)
        
        total_equipment = MaintenanceEquipment.query.count()
        equipment_with_wc = MaintenanceEquipment.query.filter(MaintenanceEquipment.work_center_id.isnot(None)).count()
        
        total_requests = MaintenanceRequest.query.count()
        requests_with_wc = MaintenanceRequest.query.filter(MaintenanceRequest.work_center_id.isnot(None)).count()
        
        print(f"Work Centers: {len(work_centers)}")
        print(f"Equipment: {total_equipment} (with WC: {equipment_with_wc}, without: {total_equipment - equipment_with_wc})")
        print(f"Requests: {total_requests} (with WC: {requests_with_wc}, without: {total_requests - requests_with_wc})")
        
        print("\n[SUCCESS] Work centers merged with existing data successfully!")
        print("All existing data preserved. Work centers assigned where missing.")

if __name__ == '__main__':
    merge_work_centers_with_existing_data()

