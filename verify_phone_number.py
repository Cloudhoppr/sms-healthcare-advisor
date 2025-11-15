"""Verify a phone number in Twilio"""
import os
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

try:
    client = Client(account_sid, auth_token)
    
    # Check verified numbers
    print("Checking verified phone numbers in your Twilio account...")
    incoming_phone_numbers = client.incoming_phone_numbers.list()
    
    print(f"\nYour Twilio phone number: +18573552130")
    print(f"\nTo send SMS to +18048470893, you need to verify it first.")
    print("\nSteps to verify:")
    print("1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print("2. Click 'Add a new number'")
    print("3. Enter: +18048470893")
    print("4. Click 'Verify'")
    print("5. Enter the verification code sent to that number")
    print("\nAlternatively, upgrade your Twilio account to send to any number.")
    
    # Try to list verified caller IDs (if available)
    try:
        verified_numbers = client.outgoing_caller_ids.list()
        if verified_numbers:
            print("\nCurrently verified numbers:")
            for num in verified_numbers:
                print(f"  - {num.phone_number} ({num.friendly_name})")
        else:
            print("\nNo verified numbers found.")
    except:
        pass
        
except Exception as e:
    print(f"Error: {e}")

