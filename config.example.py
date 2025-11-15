"""
Example configuration file for SMS Healthcare Advisor
Copy this to config.py and fill in your values, or use environment variables.
"""
import os

# Twilio SMS Configuration
# Get these from https://console.twilio.com/
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid_here")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token_here")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "+1234567890")

# Hugging Face Model Configuration
# Default: microsoft/DialoGPT-medium
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/DialoGPT-medium")

# Server Configuration
PORT = int(os.getenv("PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

