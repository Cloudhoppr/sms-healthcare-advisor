# Send a test SMS message
# Set your Twilio credentials here
# $env:TWILIO_ACCOUNT_SID = "your_account_sid_here"
# $env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
# $env:TWILIO_FROM_NUMBER = "+1234567890"

# Set recipient number
$toNumber = "+1234567890"
$message = "Hello! This is your SMS Healthcare Advisor. I'm ready to help with health questions. Try asking me about symptoms, conditions, or general health advice. For example: 'I have a headache' or 'What are the symptoms of a cold?'"

$body = @{
    to = $toNumber
    message = $message
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/sms/send" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.success) {
        Write-Host "✓ SMS sent successfully!" -ForegroundColor Green
        Write-Host "  Message SID: $($result.message_sid)" -ForegroundColor Cyan
        Write-Host "  Status: $($result.status)" -ForegroundColor Cyan
        Write-Host "  To: $($result.to)" -ForegroundColor Cyan
    } else {
        Write-Host "✗ Failed to send SMS" -ForegroundColor Red
        Write-Host "  Error: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "Error sending SMS: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Yellow
    }
}

