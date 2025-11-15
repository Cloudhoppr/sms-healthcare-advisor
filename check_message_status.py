"""Check SMS message status"""
import os
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    # Check the message we just sent
    message_sid = "SM67ac2a27b91f43f1c20b1b6b0b892670"
    message = client.messages(message_sid).fetch()
    
    print(f"Message Status: {message.status}")
    print(f"To: {message.to}")
    print(f"From: {message.from_}")
    print(f"Body: {message.body}")
    print(f"Error Code: {message.error_code}")
    print(f"Error Message: {message.error_message}")
    print(f"Date Sent: {message.date_sent}")
    
    if message.status == "failed":
        print("\nMessage failed to send!")
        print(f"Error: {message.error_message}")
    elif message.status == "queued":
        print("\nMessage is still queued. It may take a moment to send.")
    elif message.status == "sent":
        print("\nMessage was sent successfully. Check your phone.")
    elif message.status == "delivered":
        print("\nMessage was delivered successfully!")
        
except Exception as e:
    print(f"Error checking message: {e}")
    
    # Try to list recent messages
    try:
        print("\nChecking recent messages...")
        messages = client.messages.list(limit=5)
        print(f"\nRecent messages ({len(messages)}):")
        for msg in messages:
            print(f"  To: {msg.to}, Status: {msg.status}, Date: {msg.date_sent}")
    except Exception as e2:
        print(f"Error listing messages: {e2}")

