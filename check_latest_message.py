"""Check the latest SMS message status"""
import os
import time
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    # Get message SID from command line or use latest
    import sys
    message_sid = sys.argv[1] if len(sys.argv) > 1 else None
    if not message_sid:
        # Get latest message
        messages = client.messages.list(limit=1)
        if messages:
            message_sid = messages[0].sid
        else:
            print("No messages found")
            exit(1)
    
    print("Checking latest message status...")
    time.sleep(3)  # Wait for status to update
    
    message = client.messages(message_sid).fetch()
    
    print(f"\nMessage Status: {message.status}")
    print(f"To: {message.to}")
    print(f"From: {message.from_}")
    
    if message.error_code:
        print(f"Error Code: {message.error_code}")
        print(f"Error Message: {message.error_message}")
    
    status_colors = {
        "queued": "yellow",
        "sent": "green", 
        "delivered": "green",
        "failed": "red",
        "undelivered": "red"
    }
    
    status = message.status.lower()
    print(f"\nStatus: {status.upper()}")
    
    if status == "delivered":
        print("\nSUCCESS! Message was delivered. Check your phone!")
    elif status == "sent":
        print("\nMessage was sent! It should arrive shortly. Check your phone.")
    elif status == "queued":
        print("\nMessage is still queued. Please wait a moment and check your phone.")
    elif status in ["failed", "undelivered"]:
        print(f"\nMessage not delivered. Error code: {message.error_code}")
        print("\nPlease check:")
        print("1. Your phone can receive SMS")
        print("2. No carrier blocking")
        print("3. Twilio Console logs for details")
        
except Exception as e:
    print(f"Error: {e}")

