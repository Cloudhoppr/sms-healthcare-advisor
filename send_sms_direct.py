"""Send SMS directly using Twilio client"""
import os
from sms_service import SMSService

# Set credentials
# Credentials should be set as environment variables
# Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER before running

try:
    # Initialize SMS service
    sms = SMSService()
    
    # Send message
    to_number = "+18048470893"
    message = "Hello! This is your SMS Healthcare Advisor. I'm ready to help with health questions. Try asking me about symptoms, conditions, or general health advice. For example: 'I have a headache' or 'What are the symptoms of a cold?'"
    
    print(f"Sending SMS to {to_number}...")
    result = sms.send_sms(to_number, message)
    
    if result["success"]:
        print("SMS sent successfully!")
        print(f"  Message SID: {result['message_sid']}")
        print(f"  Status: {result['status']}")
        print(f"  To: {result['to']}")
    else:
        print("Failed to send SMS")
        print(f"  Error: {result['error']}")
        
except Exception as e:
    print(f"Error: {e}")

