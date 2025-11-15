# Start SMS Healthcare Advisor Server
# This script sets environment variables and starts the server

# Set your Twilio credentials here
# $env:TWILIO_ACCOUNT_SID = "your_account_sid_here"
# $env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
# $env:TWILIO_FROM_NUMBER = "+1234567890"

Write-Host "Starting SMS Healthcare Advisor Server..." -ForegroundColor Cyan
Write-Host "Twilio credentials configured." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Yellow
Write-Host "  - Health check: http://localhost:5000/" -ForegroundColor Yellow
Write-Host "  - SMS webhook: http://localhost:5000/sms/webhook" -ForegroundColor Yellow
Write-Host "  - Test endpoint: http://localhost:5000/sms/test" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

python sms_server.py

