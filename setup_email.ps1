# GearGuard Email Configuration Script
# Run this script to set up email credentials

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GearGuard Email Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if credentials are already set
$currentUser = $env:MAIL_USERNAME
$currentPass = $env:MAIL_PASSWORD

if ($currentUser -and $currentPass) {
    Write-Host "Current email configuration:" -ForegroundColor Yellow
    Write-Host "  MAIL_USERNAME: $currentUser" -ForegroundColor Green
    Write-Host "  MAIL_PASSWORD: [HIDDEN]" -ForegroundColor Green
    Write-Host ""
    $change = Read-Host "Do you want to change it? (y/n)"
    if ($change -ne "y" -and $change -ne "Y") {
        Write-Host "Keeping existing configuration." -ForegroundColor Green
        exit
    }
}

Write-Host "Email Setup Instructions:" -ForegroundColor Yellow
Write-Host "1. For Gmail: Enable 2FA and generate App Password" -ForegroundColor White
Write-Host "   Visit: https://myaccount.google.com/apppasswords" -ForegroundColor White
Write-Host "2. For other providers: Use your SMTP credentials" -ForegroundColor White
Write-Host ""

$email = Read-Host "Enter your email address"
$password = Read-Host "Enter your email password (or App Password for Gmail)" -AsSecureString
$passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Set environment variables for current session
$env:MAIL_USERNAME = $email
$env:MAIL_PASSWORD = $passwordPlain

Write-Host ""
Write-Host "Email credentials set for this session!" -ForegroundColor Green
Write-Host "  MAIL_USERNAME: $email" -ForegroundColor Green
Write-Host "  MAIL_PASSWORD: [SET]" -ForegroundColor Green
Write-Host ""
Write-Host "To make this permanent, add to your PowerShell profile:" -ForegroundColor Yellow
Write-Host "  `$env:MAIL_USERNAME='$email'" -ForegroundColor White
Write-Host "  `$env:MAIL_PASSWORD='$passwordPlain'" -ForegroundColor White
Write-Host ""
Write-Host "Or set system environment variables in Windows Settings." -ForegroundColor Yellow
Write-Host ""
Write-Host "Testing email configuration..." -ForegroundColor Cyan

# Test the configuration
python test_email_config.py

Write-Host ""
Write-Host "You can now run the application and emails will be sent!" -ForegroundColor Green
Write-Host "Start the app with: python app.py" -ForegroundColor Cyan

