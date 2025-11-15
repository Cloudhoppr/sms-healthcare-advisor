"""Diagnose Twilio SMS issues"""
import os
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    print("=== Twilio Account Diagnosis ===\n")
    
    # Get account info
    account = client.api.accounts(account_sid).fetch()
    print(f"Account Status: {account.status}")
    print(f"Account Type: {'Trial' if account.status == 'trial' else 'Paid'}")
    
    # Check recent messages
    print("\n=== Recent Messages (last 5) ===")
    messages = client.messages.list(limit=5)
    
    for msg in messages:
        print(f"\nTo: {msg.to}")
        print(f"  Status: {msg.status}")
        print(f"  Date: {msg.date_sent}")
        if msg.error_code:
            print(f"  Error Code: {msg.error_code}")
            print(f"  Error Message: {msg.error_message}")
    
    # Check phone number capabilities
    print("\n=== Your Twilio Number ===")
    phone_number = client.incoming_phone_numbers.list(phone_number="+18573552130")
    if phone_number:
        pn = phone_number[0]
        print(f"Number: {pn.phone_number}")
        print(f"Capabilities: {pn.capabilities}")
    
    print("\n=== Recommendations ===")
    print("1. Try sending from Twilio Console to isolate the issue")
    print("2. Check if +18048470893 is a mobile number (not landline)")
    print("3. Verify your carrier isn't blocking Twilio messages")
    print("4. Check Twilio logs for detailed error: https://console.twilio.com/us1/monitor/logs/sms")
    
except Exception as e:
    print(f"Error: {e}")

