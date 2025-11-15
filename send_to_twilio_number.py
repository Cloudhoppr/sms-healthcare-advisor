"""Send SMS to the Twilio number to test webhook"""
import os
from sms_service import SMSService

# Set credentials
# Credentials should be set as environment variables
# Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER before running

try:
    sms = SMSService()
    
    # Send to the Twilio number itself
    to_number = "+18573552130"
    message = "I have a headache"
    
    print(f"Sending SMS to {to_number}...")
    print(f"Message: {message}")
    print("\nNote: This will only work if you have a webhook configured.")
    print("The webhook should point to: http://your-server/sms/webhook")
    print()
    
    result = sms.send_sms(to_number, message)
    
    if result["success"]:
        print("SMS sent successfully!")
        print(f"  Message SID: {result['message_sid']}")
        print(f"  Status: {result['status']}")
        print(f"  To: {result['to']}")
        print("\nIf webhook is configured, the Healthcare Advisor should respond automatically.")
    else:
        print(f"Failed to send SMS: {result['error']}")
        
except Exception as e:
    print(f"Error: {e}")

