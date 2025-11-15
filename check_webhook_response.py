"""Check if webhook processed the latest message and what response was sent"""
import os
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    print("=== Latest Incoming Message ===")
    
    # Get the most recent inbound message
    messages = client.messages.list(limit=5)
    
    for msg in messages:
        if msg.direction == "inbound":
            print(f"\nINBOUND Message:")
            print(f"  From: {msg.from_}")
            print(f"  To: {msg.to}")
            print(f"  Body: {msg.body}")
            print(f"  Status: {msg.status}")
            print(f"  Date: {msg.date_sent or msg.date_created}")
            
            # Check if there was a response
            print(f"\nChecking for response...")
            break
    
    # Check for the corresponding outbound response
    print("\n=== Response Attempted ===")
    for msg in messages:
        if msg.direction == "outbound" and msg.to == "+18048470893":
            print(f"\nOUTBOUND Response:")
            print(f"  To: {msg.to}")
            print(f"  Status: {msg.status}")
            print(f"  Body: {msg.body}")
            if msg.error_code:
                print(f"  Error Code: {msg.error_code}")
                print(f"  Error Message: {msg.error_message}")
            break
    
    print("\n=== Webhook Status ===")
    print("If webhook is configured, Twilio should have called your server.")
    print("Check your server logs to see if the webhook was processed.")
    print("\nTo configure webhook:")
    print("1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active")
    print("2. Click on +18573552130")
    print("3. Set webhook URL to your server's /sms/webhook endpoint")
    
except Exception as e:
    print(f"Error: {e}")

