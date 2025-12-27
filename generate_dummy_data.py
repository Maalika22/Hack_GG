"""
Generate 500 IT-related dummy data records for GearGuard
This script creates comprehensive test data showcasing all functionality
"""

from models import (
    db, User, Department, MaintenanceCategory, MaintenanceTeam,
    MaintenanceEquipment, MaintenanceRequest, Company, WorkCenter
)
from decimal import Decimal
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import random

# Real-life first names
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Andrew", "Emily", "Paul", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Jason", "Rebecca", "Edward", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Alexander", "Debra",
    "Patrick", "Rachel", "Frank", "Carolyn", "Raymond", "Janet", "Jack", "Virginia",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Julie",
    "Jose", "Joyce", "Adam", "Victoria", "Nathan", "Kelly", "Henry", "Christina",
    "Douglas", "Joan", "Zachary", "Evelyn", "Peter", "Judith", "Kyle", "Megan",
    "Noah", "Cheryl", "Ethan", "Andrea", "Jeremy", "Hannah", "Walter", "Jacqueline",
    "Christian", "Martha", "Keith", "Gloria", "Roger", "Teresa", "Terry", "Sara",
    "Austin", "Janice", "Sean", "Marie", "Gerald", "Julia", "Carl", "Grace",
    "Harold", "Judy", "Dylan", "Theresa", "Louis", "Madison", "Wayne", "Beverly",
    "Eugene", "Denise", "Jordan", "Marilyn", "Arthur", "Amber", "Juan", "Danielle",
    "Lawrence", "Brittany", "Willie", "Diana", "Alan", "Abigail", "Ralph", "Jane",
    "Randy", "Lori", "Roy", "Kathryn", "Vincent", "Alexis", "Russell", "Tiffany",
    "Bobby", "Kayla", "Mason", "Natalie", "Philip", "Olivia", "Johnny", "Kristin"
]

# Real-life last names
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
    "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez",
    "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams",
    "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards",
    "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers",
    "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", "Reed", "Kelly",
    "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks",
    "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross",
    "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell",
    "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez", "Simmons",
    "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham", "Reynolds", "Griffin",
    "Wallace", "Moreno", "West", "Hayes", "Chavez", "Gibson", "Bryant", "Ellis",
    "Stevens", "Murray", "Ford", "Marshall", "Owens", "Mcdonald", "Harrison", "Ruiz",
    "Kennedy", "Wells", "Alvarez", "Woods", "Mendoza", "Stone", "Hawkins", "Dunn",
    "Perkins", "Hudson", "Spencer", "Gardner", "Stephens", "Payne", "Pierce", "Berry",
    "Matthews", "Arnold", "Wagner", "Willis", "Ray", "Watkins", "Olson", "Carroll",
    "Duncan", "Snyder", "Hart", "Cunningham", "Bradley", "Lane", "Andrews", "Ruiz",
    "Harper", "Fox", "Riley", "Armstrong", "Carpenter", "Weaver", "Greene", "Lawrence",
    "Elliott", "Chavez", "Sims", "Austin", "Peters", "Kelley", "Franklin", "Lawson"
]

# Companies by product type
COMPANIES_BY_CATEGORY = {
    "Desktop Computers": [
        {"name": "Dell Technologies Inc.", "address": "One Dell Way, Round Rock, TX 78682", "email": "support@dell.com", "phone": "+1-800-999-3355"},
        {"name": "HP Inc.", "address": "1501 Page Mill Road, Palo Alto, CA 94304", "email": "support@hp.com", "phone": "+1-800-752-0900"},
        {"name": "Lenovo Group Limited", "address": "1009 Think Place, Morrisville, NC 27560", "email": "support@lenovo.com", "phone": "+1-866-968-4465"}
    ],
    "Laptops": [
        {"name": "Apple Inc.", "address": "One Apple Park Way, Cupertino, CA 95014", "email": "support@apple.com", "phone": "+1-800-275-2273"},
        {"name": "Microsoft Corporation", "address": "One Microsoft Way, Redmond, WA 98052", "email": "support@microsoft.com", "phone": "+1-800-642-7676"},
        {"name": "ASUS Computer International", "address": "48720 Kato Road, Fremont, CA 94538", "email": "support@asus.com", "phone": "+1-510-739-3777"}
    ],
    "Servers": [
        {"name": "Dell Technologies Inc.", "address": "One Dell Way, Round Rock, TX 78682", "email": "enterprise@dell.com", "phone": "+1-800-999-3355"},
        {"name": "Hewlett Packard Enterprise", "address": "6280 America Center Drive, San Jose, CA 95002", "email": "support@hpe.com", "phone": "+1-800-752-0900"},
        {"name": "IBM Corporation", "address": "1 New Orchard Road, Armonk, NY 10504", "email": "support@ibm.com", "phone": "+1-800-426-4968"}
    ],
    "Network Equipment": [
        {"name": "Cisco Systems Inc.", "address": "170 West Tasman Drive, San Jose, CA 95134", "email": "support@cisco.com", "phone": "+1-800-553-6387"},
        {"name": "Juniper Networks Inc.", "address": "1133 Innovation Way, Sunnyvale, CA 94089", "email": "support@juniper.net", "phone": "+1-888-586-4737"},
        {"name": "Aruba Networks", "address": "1322 Crossman Avenue, Sunnyvale, CA 94089", "email": "support@arubanetworks.com", "phone": "+1-408-227-4500"}
    ],
    "Printers & Scanners": [
        {"name": "Canon Inc.", "address": "One Canon Park, Melville, NY 11747", "email": "support@canon.com", "phone": "+1-800-652-2666"},
        {"name": "Epson America Inc.", "address": "3131 Katella Avenue, Los Alamitos, CA 90720", "email": "support@epson.com", "phone": "+1-800-463-7766"},
        {"name": "Xerox Corporation", "address": "201 Merritt 7, Norwalk, CT 06851", "email": "support@xerox.com", "phone": "+1-800-275-9376"}
    ],
    "Monitors": [
        {"name": "LG Electronics USA", "address": "1000 Sylvan Avenue, Englewood Cliffs, NJ 07632", "email": "support@lg.com", "phone": "+1-800-243-0000"},
        {"name": "Samsung Electronics America", "address": "85 Challenger Road, Ridgefield Park, NJ 07660", "email": "support@samsung.com", "phone": "+1-800-726-7864"},
        {"name": "Acer America Corporation", "address": "1731 Technology Drive, San Jose, CA 95110", "email": "support@acer.com", "phone": "+1-866-695-2237"}
    ],
    "Storage Devices": [
        {"name": "Western Digital Corporation", "address": "5601 Great Oaks Parkway, San Jose, CA 95119", "email": "support@wdc.com", "phone": "+1-800-275-4932"},
        {"name": "Seagate Technology LLC", "address": "10200 South De Anza Boulevard, Cupertino, CA 95014", "email": "support@seagate.com", "phone": "+1-800-732-4283"},
        {"name": "SanDisk Corporation", "address": "601 McCarthy Boulevard, Milpitas, CA 95035", "email": "support@sandisk.com", "phone": "+1-866-726-3475"}
    ],
    "Security Equipment": [
        {"name": "Fortinet Inc.", "address": "899 Kifer Road, Sunnyvale, CA 94086", "email": "support@fortinet.com", "phone": "+1-408-235-7700"},
        {"name": "Palo Alto Networks Inc.", "address": "3000 Tannery Way, Santa Clara, CA 95054", "email": "support@paloaltonetworks.com", "phone": "+1-866-320-4788"},
        {"name": "Check Point Software Technologies", "address": "5 Ha'Solelim Street, Tel Aviv, Israel", "email": "support@checkpoint.com", "phone": "+1-650-628-2000"}
    ],
    "UPS Systems": [
        {"name": "APC by Schneider Electric", "address": "132 Fairgrounds Road, West Kingston, RI 02892", "email": "support@apc.com", "phone": "+1-800-877-4080"},
        {"name": "CyberPower Systems Inc.", "address": "4241 12th Avenue East, Shakopee, MN 55379", "email": "support@cyberpowersystems.com", "phone": "+1-888-937-9977"},
        {"name": "Tripp Lite", "address": "1111 West 35th Street, Chicago, IL 60609", "email": "support@tripplite.com", "phone": "+1-773-869-1234"}
    ],
    "Network Storage": [
        {"name": "Synology Inc.", "address": "4F, No. 1, Yuanqu Street, Nangang District, Taipei, Taiwan", "email": "support@synology.com", "phone": "+1-510-265-1122"},
        {"name": "QNAP Systems Inc.", "address": "No. 1, Yuanqu Street, Nangang District, Taipei, Taiwan", "email": "support@qnap.com", "phone": "+1-909-595-2816"},
        {"name": "Netgear Inc.", "address": "350 East Plumeria Drive, San Jose, CA 95134", "email": "support@netgear.com", "phone": "+1-888-638-4327"}
    ]
}

# IT Equipment Names
IT_EQUIPMENT = [
    "Dell OptiPlex 7090", "HP EliteDesk 800", "Lenovo ThinkCentre M90",
    "MacBook Pro 16", "MacBook Air M2", "Surface Pro 9",
    "Dell Latitude 5520", "HP ZBook Studio", "ThinkPad X1 Carbon",
    "Server Rack Unit 1", "Server Rack Unit 2", "Dell PowerEdge R740",
    "HP ProLiant DL380", "Cisco Catalyst Switch", "Netgear ProSafe Switch",
    "Ubiquiti Access Point", "Aruba Access Point", "Meraki Access Point",
    "Canon ImageRunner", "HP LaserJet Pro", "Brother MFC-L3770",
    "Epson WorkForce Pro", "Xerox VersaLink", "Konica Minolta Bizhub",
    "Samsung Galaxy Tab", "iPad Pro 12.9", "Microsoft Surface Go",
    "Dell Monitor 27", "LG UltraWide Monitor", "Samsung 4K Monitor",
    "Logitech MX Master", "Microsoft Surface Mouse", "Apple Magic Mouse",
    "Blue Yeti Microphone", "Logitech Webcam C920", "Jabra Speak 710",
    "Dell Docking Station", "HP Thunderbolt Dock", "CalDigit TS3 Plus",
    "APC UPS 1500VA", "CyberPower UPS 1000VA", "Tripp Lite UPS 1500VA",
    "Western Digital NAS", "Synology DiskStation", "QNAP TS-453D",
    "Seagate External Drive", "Samsung T7 SSD", "SanDisk Extreme SSD",
    "Cisco Router 2900", "Fortinet Firewall", "Palo Alto Firewall",
    "Dell OptiPlex 3080", "HP ProDesk 400", "Lenovo ThinkStation P340"
]

# Vendor company names
VENDOR_COMPANIES = [
    "TechSupply Solutions", "Global IT Distributors", "Enterprise Hardware Co.",
    "Digital Equipment Suppliers", "IT Infrastructure Partners", "Computer Systems Inc.",
    "Network Solutions Group", "Hardware Direct LLC", "Tech Components Ltd.",
    "IT Equipment Warehouse", "Business Technology Supply", "Corporate IT Solutions",
    "Enterprise Tech Distributors", "Professional IT Supply", "Technology Partners Inc."
]

# IT Categories
IT_CATEGORIES = [
    "Desktop Computers", "Laptops", "Servers", "Network Equipment",
    "Printers & Scanners", "Tablets", "Monitors", "Peripherals",
    "Audio/Video Equipment", "Storage Devices", "Security Equipment",
    "Docking Stations", "UPS Systems", "Network Storage"
]

# IT Teams
IT_TEAMS = [
    "IT Support Level 1", "IT Support Level 2", "Network Administration",
    "Server Administration", "Security Team", "Hardware Maintenance",
    "Software Support", "Infrastructure Team"
]

# Departments
DEPARTMENTS = [
    "IT Department", "Development", "QA Testing", "DevOps",
    "Network Operations", "Security Operations", "Help Desk",
    "System Administration", "Database Administration", "Cloud Operations"
]

# Work Center Names
WORK_CENTERS = [
    "Assembly 1", "Assembly 2", "Drill 1", "Drill 2", "Welding Station 1",
    "Welding Station 2", "CNC Machine 1", "CNC Machine 2", "Lathe 1", "Lathe 2",
    "Milling Machine 1", "Milling Machine 2", "Testing Station 1", "Testing Station 2",
    "Quality Control 1", "Quality Control 2", "Packaging Line 1", "Packaging Line 2",
    "Inspection Bay 1", "Inspection Bay 2", "Repair Station 1", "Repair Station 2",
    "Calibration Lab", "Maintenance Bay 1", "Maintenance Bay 2"
]

# Request Subjects
REQUEST_SUBJECTS = [
    "Computer not booting", "Slow performance", "Blue screen error",
    "Network connectivity issues", "Printer not printing", "Monitor display issues",
    "Keyboard not working", "Mouse not responding", "Software installation needed",
    "Password reset required", "Email configuration", "VPN connection problem",
    "Server down", "Database connection error", "Application crash",
    "Hard drive failure", "RAM upgrade needed", "OS reinstallation",
    "Antivirus update", "Firewall configuration", "Backup restoration",
    "Data recovery", "Hardware upgrade", "Driver installation",
    "BIOS update", "Firmware update", "Security patch installation",
    "Disk cleanup needed", "Memory leak", "Performance optimization"
]

def generate_requests_only():
    """Generate requests only - for adding requests to existing data"""
    print("Generating maintenance requests...")
    
    # Get existing data
    equipment_list = MaintenanceEquipment.query.all()
    workers = User.query.filter_by(is_admin=False, is_active=True).all()
    work_centers = WorkCenter.query.all()
    
    if not equipment_list:
        print("[ERROR] No equipment found. Please generate equipment first.")
        return
    
    if not workers:
        print("[ERROR] No workers found. Please generate workers first.")
        return
    
    # Clear existing requests first
    existing_requests = MaintenanceRequest.query.count()
    if existing_requests > 0:
        print(f"[INFO] Clearing {existing_requests} existing requests...")
        MaintenanceRequest.query.delete()
        db.session.commit()
    
    # Create maintenance requests (500 requests showcasing various scenarios)
    request_count = 0
    
    # Distribution: 30% new, 25% in_progress, 40% repaired, 5% scrap
    stage_distribution = ['new'] * 150 + ['in_progress'] * 125 + ['repaired'] * 200 + ['scrap'] * 25
    random.shuffle(stage_distribution)
    
    print("Creating maintenance requests with various scenarios...")
    
    for i in range(500):
        eq = random.choice(equipment_list)
        request_type = random.choice(['corrective', 'preventive'])
        stage = stage_distribution[i] if i < len(stage_distribution) else random.choice(['new', 'in_progress', 'repaired', 'scrap'])
        
        # Generate unique request name
        request_name = f'MR{request_count + 1:05d}'
        
        # Select worker for allocation (vary allocation scenarios)
        allocated_worker = None
        if random.random() > 0.2:  # 80% allocated
            allocated_worker = random.choice(workers)
        
        # Create request
        req = MaintenanceRequest(
            name=request_name,
            subject=random.choice(REQUEST_SUBJECTS),
            request_type=request_type,
            equipment_id=eq.id,
            category_id=eq.category_id,
            team_id=eq.team_id,
            stage=stage,
            allocated_to_id=allocated_worker.id if allocated_worker else None,
            technician_id=eq.technician_id if random.random() > 0.3 else (allocated_worker.id if allocated_worker else None),
            assigned_user_id=allocated_worker.id if allocated_worker and random.random() > 0.3 else None,
            maintenance_for_id=random.choice(workers).id if workers and random.random() > 0.4 else None,  # Maintenance For field
            work_center_id=eq.work_center_id if eq.work_center_id and random.random() > 0.2 else (random.choice(work_centers).id if work_centers and random.random() > 0.5 else None)  # Work Center
        )
        
        # Set allocation status and workflow based on stage
        if stage == 'new':
            req.allocation_status = 'pending' if not allocated_worker else 'allocated'
        elif stage == 'in_progress':
            # Mix of allocation statuses for in_progress
            if allocated_worker:
                req.allocation_status = random.choice(['allocated', 'accepted', 'in_progress'])
                if req.allocation_status in ['accepted', 'in_progress']:
                    req.worker_response = 'accepted'
                    req.worker_response_at = datetime.utcnow() - timedelta(days=random.randint(1, 15))
                    req.worker_response_reason = random.choice([
                        'Accepted and ready to start',
                        'Will begin work immediately',
                        'Equipment accessible, can proceed',
                        'All resources available'
                    ])
            else:
                req.allocation_status = 'pending'
        elif stage == 'repaired':
            req.allocation_status = 'completed'
            if allocated_worker:
                req.worker_response = 'accepted'
                req.worker_response_at = datetime.utcnow() - timedelta(days=random.randint(5, 30))
        elif stage == 'scrap':
            req.allocation_status = 'completed'
        
        # Set dates based on stage and type
        if request_type == 'preventive':
            req.scheduled_date = datetime.utcnow() + timedelta(days=random.randint(-60, 60))
        
        # Set start/end dates for in_progress and repaired
        if stage in ['in_progress', 'repaired']:
            days_ago_start = random.randint(1, 45)
            req.start_date = datetime.utcnow() - timedelta(days=days_ago_start)
            
            if allocated_worker:
                req.allocated_at = datetime.utcnow() - timedelta(days=days_ago_start + random.randint(1, 10))
        
        if stage == 'repaired':
            days_ago_end = random.randint(1, 30)
            req.end_date = datetime.utcnow() - timedelta(days=days_ago_end)
            # Duration between start and end
            if req.start_date:
                delta = req.end_date - req.start_date
                req.duration = max(0.5, delta.total_seconds() / 3600.0)
            else:
                req.duration = random.uniform(0.5, 12.0)
        
        # Add deadline proposals for some allocated requests (showcase deadline workflow)
        if allocated_worker and req.allocation_status in ['allocated', 'accepted']:
            if random.random() > 0.6:  # 40% have deadline proposals
                req.proposed_deadline = datetime.utcnow() + timedelta(days=random.randint(1, 21))
                req.deadline_status = random.choice(['pending', 'approved', 'rejected'])
                
                if req.deadline_status == 'approved':
                    req.deadline_approved_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                    req.admin_instructions = random.choice([
                        'Please ensure all safety protocols are followed',
                        'Complete documentation required',
                        'Priority: High - Complete within deadline',
                        'Standard maintenance procedures apply'
                    ])
                elif req.deadline_status == 'rejected':
                    req.deadline_admin_response = random.choice([
                        'Deadline too far out, need completion sooner',
                        'Please propose earlier date',
                        'Urgent request, must complete within 3 days'
                    ])
        
        # Add some overdue requests (showcase overdue functionality)
        if stage in ['new', 'in_progress'] and req.scheduled_date:
            if random.random() > 0.85:  # 15% overdue
                req.scheduled_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        db.session.add(req)
        request_count += 1
        
        # Commit in batches
        if request_count % 100 == 0:
            db.session.commit()
            print(f"Created {request_count} requests...")
    
    db.session.commit()
    
    # Calculate statistics
    new_requests = MaintenanceRequest.query.filter_by(stage='new').count()
    in_progress_requests = MaintenanceRequest.query.filter_by(stage='in_progress').count()
    repaired_requests = MaintenanceRequest.query.filter_by(stage='repaired').count()
    scrap_requests = MaintenanceRequest.query.filter_by(stage='scrap').count()
    
    pending_allocation = MaintenanceRequest.query.filter_by(allocation_status='pending').count()
    allocated_requests = MaintenanceRequest.query.filter_by(allocation_status='allocated').count()
    accepted_requests = MaintenanceRequest.query.filter_by(allocation_status='accepted').count()
    completed_requests = MaintenanceRequest.query.filter_by(allocation_status='completed').count()
    
    overdue_count = len([r for r in MaintenanceRequest.query.all() if r.is_overdue])
    
    print(f"\n[OK] Request generation complete!")
    print(f"   - Total Requests: {request_count}")
    print(f"\nRequest Status Distribution:")
    print(f"   - New: {new_requests}")
    print(f"   - In Progress: {in_progress_requests}")
    print(f"   - Repaired: {repaired_requests}")
    print(f"   - Scrap: {scrap_requests}")
    print(f"\nAllocation Status:")
    print(f"   - Pending: {pending_allocation}")
    print(f"   - Allocated: {allocated_requests}")
    print(f"   - Accepted: {accepted_requests}")
    print(f"   - Completed: {completed_requests}")
    print(f"   - Overdue: {overdue_count}")

def generate_dummy_data():
    """Generate 500 IT-related records - must be called within app context"""
    print("Starting dummy data generation...")
    
    # Check if equipment already exists (main indicator of dummy data)
    existing_equipment = MaintenanceEquipment.query.count()
    
    if existing_equipment > 0:
        print(f"[INFO] Equipment already exists ({existing_equipment} pieces)")
        print("[INFO] Generating requests only...")
        generate_requests_only()
        return
    
    # Create main company first
    main_company = Company.query.filter_by(name="TechCorp IT Solutions").first()
    if not main_company:
        main_company = Company(
            name="TechCorp IT Solutions",
            address="123 Tech Street, San Francisco, CA 94105",
            phone="+1-555-0100",
            email="info@techcorp.com"
        )
        db.session.add(main_company)
        db.session.commit()
    
    # Create companies based on categories
    companies_map = {}  # Map category name to company
    all_companies = [main_company]
    
    # Create companies for each category type
    for category_name in IT_CATEGORIES:
        if category_name in COMPANIES_BY_CATEGORY:
            company_data = random.choice(COMPANIES_BY_CATEGORY[category_name])
            company = Company.query.filter_by(name=company_data["name"]).first()
            if not company:
                company = Company(
                    name=company_data["name"],
                    address=company_data["address"],
                    phone=company_data["phone"],
                    email=company_data["email"]
                )
                db.session.add(company)
                all_companies.append(company)
            companies_map[category_name] = company
    
    db.session.commit()
    
    # Create departments
    departments = []
    for dept_name in DEPARTMENTS:
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            dept = Department(name=dept_name, description=f"{dept_name} department")
            db.session.add(dept)
            departments.append(dept)
        else:
            departments.append(dept)
    db.session.commit()
    
    # Create categories with appropriate companies
    categories = []
    for cat_name in IT_CATEGORIES:
        cat = MaintenanceCategory.query.filter_by(name=cat_name).first()
        if not cat:
            # Assign company based on category, fallback to main company
            if cat_name in companies_map:
                category_company = companies_map[cat_name]
            else:
                category_company = main_company
            cat = MaintenanceCategory(name=cat_name, company_id=category_company.id)
            db.session.add(cat)
            categories.append(cat)
        else:
            categories.append(cat)
    db.session.commit()
    
    # Create teams
    teams = []
    for team_name in IT_TEAMS:
        team = MaintenanceTeam.query.filter_by(name=team_name).first()
        if not team:
            team = MaintenanceTeam(name=team_name, company_id=main_company.id)
            db.session.add(team)
            teams.append(team)
        else:
            teams.append(team)
    db.session.commit()
    
    # Create work centers with all required fields
    work_centers = []
    for i, wc_name in enumerate(WORK_CENTERS, 1):
        wc = WorkCenter.query.filter_by(name=wc_name).first()
        if not wc:
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
            work_centers.append(wc)
        else:
            work_centers.append(wc)
    db.session.commit()
    
    # Create workers (50 workers) with real names
    workers = []
    used_names = set()
    for i in range(1, 51):
        # Generate unique real name
        while True:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            if full_name not in used_names:
                used_names.add(full_name)
                break
        
        username = f"{first_name.lower()}.{last_name.lower()}{i}"
        email = f"{first_name.lower()}.{last_name.lower()}@techcorp.com"
        
        worker = User(
            username=username,
            email=email,
            password_hash=generate_password_hash("worker123"),
            full_name=full_name,
            phone=f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            position=random.choice(["IT Technician", "Network Engineer", "System Admin", "Help Desk Support", "Security Analyst"]),
            employee_id=f"EMP{i:04d}",
            department_id=random.choice(departments).id,
            company_id=main_company.id,
            is_active=True,
            is_admin=False
        )
        # Assign to random team
        worker.teams.append(random.choice(teams))
        db.session.add(worker)
        workers.append(worker)
    db.session.commit()
    
    # Create third party users (15) with real names and vendor companies
    third_parties = []
    used_vendor_names = set()
    for i in range(1, 16):
        # Generate unique real name
        while True:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            if full_name not in used_vendor_names:
                used_vendor_names.add(full_name)
                break
        
        vendor_company = random.choice(VENDOR_COMPANIES)
        username = f"{first_name.lower()}.{last_name.lower()}"
        email = f"{first_name.lower()}.{last_name.lower()}@{vendor_company.lower().replace(' ', '').replace('.', '').replace(',', '')}.com"
        
        # Create or get vendor company
        vendor_company_obj = Company.query.filter_by(name=vendor_company).first()
        if not vendor_company_obj:
            vendor_company_obj = Company(
                name=vendor_company,
                address=f"{random.randint(100, 9999)} Business Park Drive, {random.choice(['San Francisco', 'New York', 'Chicago', 'Los Angeles', 'Seattle'])}",
                email=f"info@{vendor_company.lower().replace(' ', '').replace('.', '').replace(',', '')}.com",
                phone=f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
            )
            db.session.add(vendor_company_obj)
            db.session.commit()
        
        tp = User(
            username=username,
            email=email,
            password_hash=generate_password_hash("vendor123"),
            full_name=full_name,
            phone=f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            position=random.choice(["Sales Representative", "Account Manager", "Technical Support", "Product Specialist", "Business Development"]),
            company_id=vendor_company_obj.id,
            is_active=True,
            is_third_party=True
        )
        db.session.add(tp)
        third_parties.append(tp)
    db.session.commit()
    
    # Create equipment (200 pieces) with appropriate companies based on category
    equipment_list = []
    for i in range(200):
        category = random.choice(categories)
        # Get company for this category
        eq_company = companies_map.get(category.name, main_company)
        
        # Generate realistic equipment name
        equipment_base = random.choice(IT_EQUIPMENT)
        equipment_name = f"{equipment_base} - {random.choice(['Production', 'Development', 'Testing', 'Backup', 'Primary'])}"
        
        eq = MaintenanceEquipment(
            name=equipment_name,
            serial_number=f"SN-{random.choice(['DELL', 'HP', 'LEN', 'APP', 'MS', 'CIS', 'SAM'])}-{random.randint(100000, 999999)}",
            purchase_date=date.today() - timedelta(days=random.randint(30, 1000)),
            warranty_information=f"Warranty until {date.today() + timedelta(days=random.randint(100, 1000))}",
            location=f"Building {random.choice(['A', 'B', 'C', 'D', 'E'])}, Floor {random.randint(1, 10)}, Room {random.randint(100, 500)}",
            description=f"{category.name} equipment for {random.choice(DEPARTMENTS)} department",
            assigned_date=date.today() - timedelta(days=random.randint(1, 500)),
            used_in_location=f"Office {random.choice(['North', 'South', 'East', 'West'])} Wing - {random.randint(1, 50)}",
            health_percentage=random.randint(20, 100),
            category_id=category.id,
            team_id=random.choice(teams).id,
            department_id=random.choice(departments).id,
            company_id=eq_company.id,
            work_center_id=random.choice(work_centers).id if work_centers and random.random() > 0.3 else None,
            owner_id=random.choice(workers).id if random.random() > 0.3 else None,
            technician_id=random.choice(workers).id if random.random() > 0.5 else None,
            scrap=random.random() < 0.05  # 5% scrap rate
        )
        db.session.add(eq)
        equipment_list.append(eq)
    db.session.commit()
    
    # Create maintenance requests (500 requests showcasing various scenarios)
    request_count = 0
    
    # Distribution: 30% new, 25% in_progress, 40% repaired, 5% scrap
    stage_distribution = ['new'] * 150 + ['in_progress'] * 125 + ['repaired'] * 200 + ['scrap'] * 25
    random.shuffle(stage_distribution)
    
    print("Creating maintenance requests with various scenarios...")
    
    for i in range(500):
        eq = random.choice(equipment_list)
        request_type = random.choice(['corrective', 'preventive'])
        stage = stage_distribution[i] if i < len(stage_distribution) else random.choice(['new', 'in_progress', 'repaired', 'scrap'])
        
        # Generate unique request name
        request_name = f'MR{request_count + 1:05d}'
        
        # Select worker for allocation (vary allocation scenarios)
        allocated_worker = None
        if random.random() > 0.2:  # 80% allocated
            allocated_worker = random.choice(workers)
        
        # Create request
        req = MaintenanceRequest(
            name=request_name,
            subject=random.choice(REQUEST_SUBJECTS),
            request_type=request_type,
            equipment_id=eq.id,
            category_id=eq.category_id,
            team_id=eq.team_id,
            stage=stage,
            allocated_to_id=allocated_worker.id if allocated_worker else None,
            technician_id=eq.technician_id if random.random() > 0.3 else (allocated_worker.id if allocated_worker else None),
            assigned_user_id=allocated_worker.id if allocated_worker and random.random() > 0.3 else None,
            maintenance_for_id=random.choice(workers).id if workers and random.random() > 0.4 else None,  # Maintenance For field
            work_center_id=eq.work_center_id if eq.work_center_id and random.random() > 0.2 else (random.choice(work_centers).id if work_centers and random.random() > 0.5 else None)  # Work Center
        )
        
        # Set allocation status and workflow based on stage
        if stage == 'new':
            req.allocation_status = 'pending' if not allocated_worker else 'allocated'
        elif stage == 'in_progress':
            # Mix of allocation statuses for in_progress
            if allocated_worker:
                req.allocation_status = random.choice(['allocated', 'accepted', 'in_progress'])
                if req.allocation_status in ['accepted', 'in_progress']:
                    req.worker_response = 'accepted'
                    req.worker_response_at = datetime.utcnow() - timedelta(days=random.randint(1, 15))
                    req.worker_response_reason = random.choice([
                        'Accepted and ready to start',
                        'Will begin work immediately',
                        'Equipment accessible, can proceed',
                        'All resources available'
                    ])
            else:
                req.allocation_status = 'pending'
        elif stage == 'repaired':
            req.allocation_status = 'completed'
            if allocated_worker:
                req.worker_response = 'accepted'
                req.worker_response_at = datetime.utcnow() - timedelta(days=random.randint(5, 30))
        elif stage == 'scrap':
            req.allocation_status = 'completed'
        
        # Set dates based on stage and type
        if request_type == 'preventive':
            req.scheduled_date = datetime.utcnow() + timedelta(days=random.randint(-60, 60))
        
        # Set start/end dates for in_progress and repaired
        if stage in ['in_progress', 'repaired']:
            days_ago_start = random.randint(1, 45)
            req.start_date = datetime.utcnow() - timedelta(days=days_ago_start)
            
            if allocated_worker:
                req.allocated_at = datetime.utcnow() - timedelta(days=days_ago_start + random.randint(1, 10))
        
        if stage == 'repaired':
            days_ago_end = random.randint(1, 30)
            req.end_date = datetime.utcnow() - timedelta(days=days_ago_end)
            # Duration between start and end
            if req.start_date:
                delta = req.end_date - req.start_date
                req.duration = max(0.5, delta.total_seconds() / 3600.0)
            else:
                req.duration = random.uniform(0.5, 12.0)
        
        # Add deadline proposals for some allocated requests (showcase deadline workflow)
        if allocated_worker and req.allocation_status in ['allocated', 'accepted']:
            if random.random() > 0.6:  # 40% have deadline proposals
                req.proposed_deadline = datetime.utcnow() + timedelta(days=random.randint(1, 21))
                req.deadline_status = random.choice(['pending', 'approved', 'rejected'])
                
                if req.deadline_status == 'approved':
                    req.deadline_approved_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                    req.admin_instructions = random.choice([
                        'Please ensure all safety protocols are followed',
                        'Complete documentation required',
                        'Priority: High - Complete within deadline',
                        'Standard maintenance procedures apply'
                    ])
                elif req.deadline_status == 'rejected':
                    req.deadline_admin_response = random.choice([
                        'Deadline too far out, need completion sooner',
                        'Please propose earlier date',
                        'Urgent request, must complete within 3 days'
                    ])
        
        # Add some overdue requests (showcase overdue functionality)
        if stage in ['new', 'in_progress'] and req.scheduled_date:
            if random.random() > 0.85:  # 15% overdue
                req.scheduled_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        db.session.add(req)
        request_count += 1
        
        # Commit in batches
        if request_count % 100 == 0:
            db.session.commit()
            print(f"Created {request_count} requests...")
    
    db.session.commit()
    
    # Calculate statistics
    new_requests = MaintenanceRequest.query.filter_by(stage='new').count()
    in_progress_requests = MaintenanceRequest.query.filter_by(stage='in_progress').count()
    repaired_requests = MaintenanceRequest.query.filter_by(stage='repaired').count()
    scrap_requests = MaintenanceRequest.query.filter_by(stage='scrap').count()
    
    pending_allocation = MaintenanceRequest.query.filter_by(allocation_status='pending').count()
    allocated_requests = MaintenanceRequest.query.filter_by(allocation_status='allocated').count()
    accepted_requests = MaintenanceRequest.query.filter_by(allocation_status='accepted').count()
    completed_requests = MaintenanceRequest.query.filter_by(allocation_status='completed').count()
    
    overdue_count = len([r for r in MaintenanceRequest.query.all() if r.is_overdue])
    
    print(f"\n[OK] Dummy data generation complete!")
    print(f"   - Departments: {len(departments)}")
    print(f"   - Categories: {len(categories)}")
    print(f"   - Teams: {len(teams)}")
    print(f"   - Workers: {len(workers)}")
    print(f"   - Third Party Users: {len(third_parties)}")
    print(f"   - Equipment: {len(equipment_list)}")
    print(f"   - Maintenance Requests: {request_count}")
    print(f"\nRequest Status Distribution:")
    print(f"   - New: {new_requests}")
    print(f"   - In Progress: {in_progress_requests}")
    print(f"   - Repaired: {repaired_requests}")
    print(f"   - Scrap: {scrap_requests}")
    print(f"\nAllocation Status:")
    print(f"   - Pending: {pending_allocation}")
    print(f"   - Allocated: {allocated_requests}")
    print(f"   - Accepted: {accepted_requests}")
    print(f"   - Completed: {completed_requests}")
    print(f"   - Overdue: {overdue_count}")
    print(f"\nTotal records created: {len(departments) + len(categories) + len(teams) + len(workers) + len(third_parties) + len(equipment_list) + request_count}")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        generate_dummy_data()
