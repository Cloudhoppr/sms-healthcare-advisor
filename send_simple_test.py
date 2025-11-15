"""Send a simple test SMS"""
import os
from sms_service import SMSService

# Set credentials
# Credentials should be set as environment variables
# Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER before running

try:
    sms = SMSService()
    
    to_number = "+18048470893"
    # Very simple test message
    message = "Test message from Healthcare Advisor"
    
    print(f"Sending simple test SMS to {to_number}...")
    result = sms.send_sms(to_number, message)
    
    if result["success"]:
        print(f"Message SID: {result['message_sid']}")
        print(f"Status: {result['status']}")
        print("\nNext steps:")
        print("1. Check your Twilio Console for detailed error info:")
        print("   https://console.twilio.com/us1/monitor/logs/sms")
        print("2. Try sending a test message from Twilio Console:")
        print("   https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms")
        print("3. Verify the phone number can receive SMS (not a landline)")
        print("4. Check if your carrier is blocking messages")
    else:
        print(f"Failed: {result['error']}")
        
except Exception as e:
    print(f"Error: {e}")

