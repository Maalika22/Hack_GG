# PowerShell script to create PostgreSQL database
# Make sure PostgreSQL service is running first!

$password = "Maalika@2004#"
$dbName = "gearguard"

Write-Host "Creating database '$dbName'..." -ForegroundColor Yellow

# Try to find psql.exe
$psqlPath = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
if (-not (Test-Path $psqlPath)) {
    Write-Host "ERROR: psql.exe not found at $psqlPath" -ForegroundColor Red
    Write-Host "Please create the database manually using pgAdmin 4:" -ForegroundColor Yellow
    Write-Host "1. Open pgAdmin 4" -ForegroundColor Cyan
    Write-Host "2. Connect to PostgreSQL server" -ForegroundColor Cyan
    Write-Host "3. Right-click 'Databases' -> Create -> Database" -ForegroundColor Cyan
    Write-Host "4. Name: gearguard" -ForegroundColor Cyan
    Write-Host "5. Click Save" -ForegroundColor Cyan
    exit 1
}

# Create database using psql
$env:PGPASSWORD = $password
$createDbCommand = "CREATE DATABASE $dbName;"

try {
    & $psqlPath -U postgres -h localhost -p 5432 -c $createDbCommand
    Write-Host "`n[OK] Database '$dbName' created successfully!" -ForegroundColor Green
    Write-Host "You can now run: python app.py" -ForegroundColor Green
} catch {
    Write-Host "`nERROR: Failed to create database" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`nPlease create the database manually using pgAdmin 4 (see instructions above)" -ForegroundColor Yellow
}

