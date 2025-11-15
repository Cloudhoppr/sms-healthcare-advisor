"""Test the webhook endpoint locally (simulates Twilio webhook)"""
import os
import requests
import json

# Simulate what Twilio sends to the webhook
webhook_url = "http://localhost:5000/sms/webhook"

# This is the format Twilio sends
form_data = {
    "From": "+18048470893",  # The sender's phone number
    "To": "+18573552130",     # Your Twilio number
    "Body": "I have a headache and feel tired",  # The message
    "MessageSid": "SMtest123",
    "AccountSid": os.getenv("TWILIO_ACCOUNT_SID", "test_account_sid")
}

print("Testing webhook endpoint locally...")
print(f"Simulating message from {form_data['From']}")
print(f"Message: {form_data['Body']}\n")

try:
    # Send as form data (like Twilio does)
    response = requests.post(webhook_url, data=form_data, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.text}")
    
    if response.status_code == 200:
        print("\nSUCCESS: Webhook is working! The advisor should respond.")
        print("This is the TwiML response that would be sent back to Twilio.")
    else:
        print(f"\nERROR: Webhook returned error status: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("✗ Error: Could not connect to server.")
    print("Make sure the server is running: python sms_server.py")
except Exception as e:
    print(f"✗ Error: {e}")

