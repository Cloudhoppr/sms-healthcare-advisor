"""View messages in Twilio account"""
import os
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    print("=== Recent Messages in Twilio Account ===\n")
    
    # Get recent messages (both sent and received)
    messages = client.messages.list(limit=10)
    
    if not messages:
        print("No messages found.")
    else:
        for msg in messages:
            direction = "INBOUND" if msg.direction == "inbound" else "OUTBOUND"
            status_icon = "[OK]" if msg.status in ["delivered", "sent", "received"] else "[ERR]"
            
            print(f"{status_icon} {direction}")
            print(f"  From: {msg.from_}")
            print(f"  To: {msg.to}")
            print(f"  Status: {msg.status}")
            print(f"  Date: {msg.date_sent or msg.date_created}")
            print(f"  Body: {msg.body[:50]}..." if len(msg.body) > 50 else f"  Body: {msg.body}")
            if msg.error_code:
                print(f"  Error: {msg.error_code} - {msg.error_message}")
            print()
    
    print("\nTo see incoming messages in Twilio Console:")
    print("1. Go to: https://console.twilio.com/us1/monitor/logs/sms")
    print("2. Or send an SMS from your phone to +18573552130")
    print("3. The message will appear in the logs and trigger the webhook")
    
except Exception as e:
    print(f"Error: {e}")

