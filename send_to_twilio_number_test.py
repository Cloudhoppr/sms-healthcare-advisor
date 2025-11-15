"""Send a test message to the Twilio number to simulate incoming SMS"""
import os
import requests

# Simulate an incoming SMS to your Twilio number
# This simulates what happens when someone sends a message TO +18573552130

webhook_url = "http://localhost:5000/sms/webhook"

# Simulate message FROM +18048470893 TO +18573552130
form_data = {
    "From": "+18048470893",      # Sender's phone number
    "To": "+18573552130",         # Your Twilio number (receiver)
    "Body": "I have a headache and feel tired",  # The message
    "MessageSid": "SMtest_incoming_123",
    "AccountSid": os.getenv("TWILIO_ACCOUNT_SID", "test_account_sid")
}

print("Simulating incoming SMS to your Twilio number...")
print(f"From: {form_data['From']}")
print(f"To: {form_data['To']} (Your Twilio number)")
print(f"Message: {form_data['Body']}\n")

try:
    # Send webhook request (simulating Twilio sending to your server)
    response = requests.post(webhook_url, data=form_data, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nHealthcare Advisor Response:\n{response.text}")
    
    if response.status_code == 200:
        print("\nSUCCESS: Message processed!")
        print("\nNote: To see this in Twilio Console as a real incoming message,")
        print("you need to actually send an SMS from your phone to +18573552130")
        print("\nThe webhook will then be called automatically by Twilio.")
    else:
        print(f"\nERROR: Webhook returned status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to server.")
    print("Make sure the server is running: python sms_server.py")
except Exception as e:
    print(f"ERROR: {e}")

