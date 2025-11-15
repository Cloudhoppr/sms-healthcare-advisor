# Twilio Configuration Script
# Run this script to set up your Twilio environment variables

# Set your Twilio credentials here
# $env:TWILIO_ACCOUNT_SID = "your_account_sid_here"
# $env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
# $env:TWILIO_FROM_NUMBER = "+1234567890"

Write-Host "Twilio Configuration Complete!" -ForegroundColor Green
Write-Host "  Account SID: $env:TWILIO_ACCOUNT_SID" -ForegroundColor Green
Write-Host "  Auth Token: $env:TWILIO_AUTH_TOKEN" -ForegroundColor Green
Write-Host "  From Number: $env:TWILIO_FROM_NUMBER" -ForegroundColor Green
Write-Host ""
Write-Host "All Twilio credentials are configured!" -ForegroundColor Cyan
Write-Host "You can now run: python sms_server.py" -ForegroundColor Cyan

