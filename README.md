# GearGuard - Standalone Maintenance Management System

## Overview

GearGuard is a **standalone Flask web application** for maintenance management that seamlessly connects **Equipment** (what is broken), **Teams** (who fix it), and **Requests** (the work to be done).

This is a complete standalone Flask web application that runs locally on your laptop.

## Quick Start

### Installation (3 Steps)

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open browser:** http://localhost:5000
   - Login: `admin` / `admin123`

**⚠️ IMPORTANT: PostgreSQL 18 is REQUIRED. SQLite is not supported.**

### PostgreSQL 18 Setup (Required)

PostgreSQL 18 must be installed and configured before running the application.

👉 **See [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) for complete PostgreSQL 18 setup instructions**

**Quick Setup:**
1. Install PostgreSQL 18 from https://www.postgresql.org/download/
2. Create database: `CREATE DATABASE gearguard;`
3. Set environment variables (see POSTGRESQL_SETUP.md)
4. Run `python app.py`

## Features

### Role-Based Access Control

- **Administrator Role**: Full system management
  - Manage equipment, requests, teams, workers, categories, departments
  - View system-wide statistics and reports
  - Create and manage worker accounts
  
- **User Role**: Limited access
  - Create maintenance requests
  - View own requests and equipment details
  - Read-only access to equipment

### Worker/Employee Management

- Complete worker profiles with:
  - Contact information (phone, email)
  - Position/Job title
  - Employee ID
  - Department assignment
  - Hire date
  - Active/Inactive status

### Core Functionality

- **Equipment Management**: Track all company assets (machines, vehicles, computers)
  - Track by Department and Employee
  - Serial numbers, purchase dates, warranty information
  - Location tracking
  - Equipment categorization

- **Maintenance Teams**: Organize technicians into specialized teams
  - Mechanics, Electricians, IT Support, etc.
  - Team member management
  - Workflow logic ensuring only team members can pick up requests

- **Maintenance Requests**: Complete lifecycle management
  - **Corrective (Breakdown)**: Unplanned repairs
  - **Preventive (Routine Checkup)**: Planned maintenance
  - Auto-fill logic when equipment is selected
  - Stage progression: New → In Progress → Repaired → Scrap

### User Interface

- **Kanban Board**: Primary workspace for technicians
  - Drag & drop between stages (visual representation)
  - Avatar display for assigned users
  - Visual indicators for overdue requests (red border)
  - Grouped by stages

- **Calendar View**: For preventive maintenance scheduling
  - Display all preventive maintenance requests
  - List view of scheduled maintenance

- **Dashboard**: Overview with statistics
  - Total equipment count
  - Total requests
  - Open requests
  - Overdue requests

### Smart Features

- **Smart Buttons**: Equipment detail shows maintenance count badge
- **Scrap Automation**: Automatically flags equipment when request moves to Scrap stage
- **Overdue Detection**: Automatic detection and visual indication of overdue requests
- **Duration Tracking**: Automatic calculation of repair duration
- **Auto-fill Logic**: Equipment selection auto-fills category, team, and technician

## Technology Stack

- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL 18** - Database (required)
- **Bootstrap 5** - Modern UI
- **Flask-Login** - Authentication
- **Flask-Mail** - Email notifications

## Requirements

- **Python 3.10 or higher**
- **PostgreSQL 18** (required - see POSTGRESQL_SETUP.md)

## Project Structure

```
GearGuard/
├── app.py                      # Main Flask application
├── models.py                   # Database models (SQLAlchemy)
├── config.py                   # Application configuration
├── routes.py                   # Core application routes
├── admin_routes.py             # Admin-specific routes
├── user_routes.py              # User-specific routes
├── worker_routes.py            # Worker-specific routes
├── decorators.py               # Access control decorators
├── email_utils.py              # Email utility functions
├── generate_dummy_data.py     # Dummy data generator (500 IT records)
├── update_database_schema.py   # Database schema migration tool
├── test_all_functionality.py   # Comprehensive test suite
├── check_utilization.py        # Utilization statistics checker
├── requirements.txt            # Python dependencies
├── START_APP.ps1              # Windows startup script
├── create_database.ps1        # Database creation script
├── templates/                 # HTML templates
│   ├── base.html
│   ├── base_admin.html
│   ├── base_user.html
│   ├── login.html
│   ├── profile.html
│   ├── admin/
│   ├── user/
│   ├── worker/
│   └── emails/
├── POSTGRESQL_SETUP.md        # PostgreSQL setup guide
├── FEATURES_IMPLEMENTED.md    # Feature documentation
├── DUMMY_DATA_SUMMARY.md      # Dummy data documentation
└── README.md                   # This file
```

## Usage

### Setting Up Equipment

1. Go to **Equipment** → **New Equipment**
2. Fill in:
   - Name and Serial Number
   - Purchase Date and Warranty Information
   - Location
   - Department and Employee Owner
   - Maintenance Team and Default Technician
   - Category

### Creating Maintenance Teams

1. Go to **Teams** → **New Team**
2. Enter team name (e.g., Mechanics, Electricians, IT Support)
3. Select team members

### Creating Maintenance Requests

#### Corrective (Breakdown) Flow

1. Go to **Requests** → **New Request**
2. Select equipment - system auto-fills category and team
3. Request starts in "New" stage
4. Click "In Progress" when work begins
5. Record duration and click "Repaired" when complete

#### Preventive (Routine Checkup) Flow

1. Go to **Requests** → **New Request**
2. Set request type to "Preventive"
3. Set scheduled date
4. Request appears in requests list

### Using the Kanban Board

- View requests grouped by stage (New, In Progress, Repaired, Scrap)
- Click on any request to view details
- Update stage using buttons on request detail page
- See overdue requests highlighted in red

## Workflows

### Breakdown Flow (Corrective)

1. User creates request with type "Corrective"
2. Selects equipment → system auto-fills category and team
3. Request starts in "New" stage
4. Manager/technician assigns themselves
5. Stage moves to "In Progress"
6. Technician records duration and moves to "Repaired"

### Routine Checkup Flow (Preventive)

1. Manager creates request with type "Preventive"
2. Sets scheduled date
3. Request appears in requests list
4. Technician picks up and executes
5. Records duration and moves to "Repaired"

## Default Login

- **Username:** `admin`
- **Password:** `admin123`

**Change this in production!**

## Running the Application

### Development Mode

```bash
python app.py
```

The application runs on `http://localhost:5000` in debug mode.

### Stop the Application

Press `Ctrl+C` in the command prompt.

## Troubleshooting

### Port 5000 already in use

Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Module not found errors

Install dependencies:
```bash
pip install -r requirements.txt
```

### Database errors

1. Ensure PostgreSQL 18 is running
2. Check database connection in `config.py` or environment variables
3. Run `update_database_schema.py` if schema is outdated
4. See POSTGRESQL_SETUP.md for detailed troubleshooting

### Can't login

The admin user is created automatically on first run. If issues:
1. Check PostgreSQL connection
2. Restart the application
3. Login with `admin` / `admin123`

## Additional Features

### Email Authentication & Notifications
- Login email notifications
- OTP-based password reset
- Work allocation email notifications
- Deadline response notifications
- Third-party product notifications

### Work Allocation System
- Admin allocates work to workers
- Workers accept/reject with reasons
- Deadline proposal workflow
- Admin deadline approval/rejection
- Utilization tracking

### Dummy Data Generation
- Automatic generation of 500 IT-related records on first run
- Includes equipment, workers, requests with various statuses
- Showcases all system functionality
- See [DUMMY_DATA_SUMMARY.md](DUMMY_DATA_SUMMARY.md) for details

### Testing
- Run comprehensive tests: `python test_all_functionality.py`
- Check utilization: `python check_utilization.py`

## Production Deployment

For production:
1. Set `debug=False` in `app.py`
2. Change `SECRET_KEY` to a random string in environment variables
3. Configure Flask-Mail with production SMTP settings
4. Use a production WSGI server (gunicorn, uWSGI)
5. Set up proper PostgreSQL connection pooling

## License

LGPL-3

## Documentation

- [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) - Complete PostgreSQL 18 setup guide
- [FEATURES_IMPLEMENTED.md](FEATURES_IMPLEMENTED.md) - Detailed feature documentation
- [DUMMY_DATA_SUMMARY.md](DUMMY_DATA_SUMMARY.md) - Dummy data generation details

---

**GearGuard** is a complete standalone Flask web application for maintenance management. It requires Python 3.10+ and PostgreSQL 18.
#   H a c k _ G G  
 #   H a c k _ G G  
 