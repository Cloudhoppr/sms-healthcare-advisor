"""Send a test SMS message"""
import os
import requests
import json

# Set environment variables
# Credentials should be set as environment variables
# Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER before running

# Send SMS via API
# Set to_number and message as needed
to_number = os.getenv("TEST_PHONE_NUMBER", "+1234567890")
message = "Hello! This is your SMS Healthcare Advisor. I'm ready to help with health questions. Try asking me about symptoms, conditions, or general health advice. For example: 'I have a headache' or 'What are the symptoms of a cold?'"

url = "http://localhost:5000/sms/send"
payload = {
    "to": to_number,
    "message": message
}

try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result.get("success"):
        print("SMS sent successfully!")
        print(f"  Message SID: {result.get('message_sid')}")
        print(f"  Status: {result.get('status')}")
        print(f"  To: {result.get('to')}")
    else:
        print("Failed to send SMS")
        print(f"  Error: {result.get('error')}")
except Exception as e:
    print(f"Error sending SMS: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")

