"""
Check utilization statistics after generating requests
"""

from app import app
from models import MaintenanceRequest, User, MaintenanceEquipment
from datetime import datetime

def check_utilization():
    """Display utilization statistics"""
    with app.app_context():
        reqs = MaintenanceRequest.query.all()
        workers = User.query.filter_by(is_admin=False, is_active=True).all()
        equipment = MaintenanceEquipment.query.all()
        
        print("\n" + "=" * 60)
        print("UTILIZATION STATISTICS")
        print("=" * 60)
        
        print(f"\nTotal Requests: {len(reqs)}")
        print(f"Total Workers: {len(workers)}")
        print(f"Total Equipment: {len(equipment)}")
        
        # Request distribution
        new_reqs = [r for r in reqs if r.stage == 'new']
        in_progress_reqs = [r for r in reqs if r.stage == 'in_progress']
        repaired_reqs = [r for r in reqs if r.stage == 'repaired']
        scrap_reqs = [r for r in reqs if r.stage == 'scrap']
        
        print(f"\nRequest Stage Distribution:")
        print(f"  New: {len(new_reqs)} ({len(new_reqs)/len(reqs)*100:.1f}%)")
        print(f"  In Progress: {len(in_progress_reqs)} ({len(in_progress_reqs)/len(reqs)*100:.1f}%)")
        print(f"  Repaired: {len(repaired_reqs)} ({len(repaired_reqs)/len(reqs)*100:.1f}%)")
        print(f"  Scrap: {len(scrap_reqs)} ({len(scrap_reqs)/len(reqs)*100:.1f}%)")
        
        # Allocation status
        pending = [r for r in reqs if r.allocation_status == 'pending']
        allocated = [r for r in reqs if r.allocation_status == 'allocated']
        accepted = [r for r in reqs if r.allocation_status == 'accepted']
        in_progress_alloc = [r for r in reqs if r.allocation_status == 'in_progress']
        completed = [r for r in reqs if r.allocation_status == 'completed']
        
        print(f"\nAllocation Status:")
        print(f"  Pending: {len(pending)}")
        print(f"  Allocated: {len(allocated)}")
        print(f"  Accepted: {len(accepted)}")
        print(f"  In Progress: {len(in_progress_alloc)}")
        print(f"  Completed: {len(completed)}")
        
        # Overdue
        overdue = [r for r in reqs if r.is_overdue]
        print(f"\nOverdue Requests: {len(overdue)}")
        
        # Worker utilization
        print(f"\nWorker Utilization (Top 15):")
        worker_utils = []
        for w in workers:
            util = w.utilization_percentage
            active_reqs = len([r for r in w.technician_requests if r.stage not in ('repaired', 'scrap')])
            worker_utils.append((w, util, active_reqs))
        
        worker_utils.sort(key=lambda x: x[1], reverse=True)
        for w, util, active in worker_utils[:15]:
            print(f"  {w.full_name or w.username}: {util}% ({active} active requests)")
        
        # Equipment with most requests
        print(f"\nEquipment with Most Requests (Top 10):")
        eq_requests = [(eq, len(eq.requests)) for eq in equipment]
        eq_requests.sort(key=lambda x: x[1], reverse=True)
        for eq, count in eq_requests[:10]:
            print(f"  {eq.name}: {count} requests")
        
        # Request types
        corrective = [r for r in reqs if r.request_type == 'corrective']
        preventive = [r for r in reqs if r.request_type == 'preventive']
        print(f"\nRequest Types:")
        print(f"  Corrective: {len(corrective)} ({len(corrective)/len(reqs)*100:.1f}%)")
        print(f"  Preventive: {len(preventive)} ({len(preventive)/len(reqs)*100:.1f}%)")
        
        # Deadline proposals
        with_deadline = [r for r in reqs if r.proposed_deadline]
        approved_deadline = [r for r in reqs if r.deadline_status == 'approved']
        rejected_deadline = [r for r in reqs if r.deadline_status == 'rejected']
        pending_deadline = [r for r in reqs if r.deadline_status == 'pending']
        
        print(f"\nDeadline Proposals:")
        print(f"  Total with Deadline: {len(with_deadline)}")
        print(f"  Approved: {len(approved_deadline)}")
        print(f"  Rejected: {len(rejected_deadline)}")
        print(f"  Pending: {len(pending_deadline)}")
        
        # Average duration
        durations = [r.duration for r in repaired_reqs if r.duration]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"\nAverage Repair Duration: {avg_duration:.2f} hours")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    check_utilization()

