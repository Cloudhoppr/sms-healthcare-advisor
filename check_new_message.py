"""Check the new SMS message status"""
import os
import time
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    # Check the new message
    message_sid = "SM744b6c8c18da15c047b5ab2becbc8a16"
    
    print("Checking message status...")
    time.sleep(2)  # Wait a moment for status to update
    
    message = client.messages(message_sid).fetch()
    
    print(f"\nMessage Status: {message.status}")
    print(f"To: {message.to}")
    print(f"From: {message.from_}")
    
    if message.error_code:
        print(f"Error Code: {message.error_code}")
        print(f"Error Message: {message.error_message}")
    
    if message.status == "failed" or message.status == "undelivered":
        print("\nTroubleshooting:")
        print("1. Check if your phone number is correct: +18048470893")
        print("2. Make sure your phone can receive SMS")
        print("3. Check if there are any carrier issues")
        print("4. Try sending from Twilio Console directly to test")
        print("\nYou can also check your Twilio logs:")
        print("https://console.twilio.com/us1/monitor/logs/sms")
    elif message.status == "queued":
        print("\nMessage is queued. It may take a few moments to send.")
        print("Please wait and check your phone.")
    elif message.status == "sent":
        print("\nMessage was sent! Check your phone for the message.")
    elif message.status == "delivered":
        print("\nMessage was delivered successfully!")
        
except Exception as e:
    print(f"Error: {e}")

