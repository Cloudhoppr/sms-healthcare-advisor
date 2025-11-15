"""
Example usage of the SMS Healthcare Advisor
Demonstrates how to use the advisor with and without SMS
"""
from llm_model import HealthcareAdvisor
from sms_service import SMSService
import os


def example_direct_usage():
    """Example of using the Healthcare Advisor directly (without SMS)."""
    print("=" * 70)
    print("Example 1: Direct Healthcare Advisor Usage")
    print("=" * 70)
    
    advisor = HealthcareAdvisor()
    
    # Example conversation
    messages = [
        "I've been feeling tired and have a runny nose",
        "I also have a cough and sore throat"
    ]
    
    for msg in messages:
        print(f"\nUser: {msg}")
        response = advisor.get_advice(msg)
        print(f"Advisor: {response}\n")
        print("-" * 70)


def example_sms_service():
    """Example of using the SMS service to send messages."""
    print("\n" + "=" * 70)
    print("Example 2: SMS Service Usage")
    print("=" * 70)
    
    try:
        # Initialize SMS service (requires Twilio credentials)
        sms = SMSService()
        
        # Send a test message
        to_number = "+1234567890"  # Replace with actual number
        message = "Hello! This is a test message from the Healthcare Advisor."
        
        print(f"\nSending SMS to {to_number}...")
        result = sms.send_sms(to_number, message)
        
        if result["success"]:
            print(f"✓ Message sent successfully!")
            print(f"  Message SID: {result['message_sid']}")
            print(f"  Status: {result['status']}")
        else:
            print(f"✗ Failed to send message: {result['error']}")
    
    except ValueError as e:
        print(f"\n⚠ SMS Service not configured: {e}")
        print("Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER")
        print("environment variables to use SMS functionality.")


def example_webhook_response():
    """Example of creating a webhook response for incoming SMS."""
    print("\n" + "=" * 70)
    print("Example 3: Webhook Response Generation")
    print("=" * 70)
    
    try:
        sms = SMSService()
        advisor = HealthcareAdvisor()
        
        # Simulate incoming SMS
        incoming_message = "What are the symptoms of a cold?"
        print(f"\nIncoming SMS: {incoming_message}")
        
        # Process with advisor
        response = advisor.process_sms(incoming_message)
        print(f"Advisor Response: {response}")
        
        # Create TwiML response
        twiml = sms.create_response(response)
        print(f"\nTwiML Response:\n{twiml}")
    
    except ValueError as e:
        print(f"\n⚠ SMS Service not configured: {e}")
        print("This example requires Twilio credentials.")


if __name__ == "__main__":
    # Run examples
    example_direct_usage()
    
    # Uncomment to test SMS functionality (requires Twilio setup)
    # example_sms_service()
    # example_webhook_response()
    
    print("\n" + "=" * 70)
    print("To test SMS functionality:")
    print("1. Set up Twilio credentials (see README.md)")
    print("2. Uncomment the SMS examples above")
    print("3. Run: python sms_server.py")
    print("=" * 70)

