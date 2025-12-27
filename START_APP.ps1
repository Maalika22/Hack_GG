# PowerShell script to start GearGuard application
# Run this script to start the application with all required environment variables

Write-Host "Starting GearGuard Application..." -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="Maalika@2004#"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="gearguard"

Write-Host "[OK] Environment variables set" -ForegroundColor Green

# Test database connection
Write-Host "Testing database connection..." -ForegroundColor Yellow
try {
    python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='gearguard', user='postgres', password='Maalika@2004#'); conn.close(); print('[OK] Database connection successful!')"
    Write-Host ""
} catch {
    Write-Host "[ERROR] Database connection failed!" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  1. PostgreSQL service is running" -ForegroundColor Yellow
    Write-Host "  2. Database 'gearguard' exists" -ForegroundColor Yellow
    Write-Host "  3. Password is correct" -ForegroundColor Yellow
    exit 1
}

# Start the application
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Write-Host "Application will be available at: http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

python app.py

