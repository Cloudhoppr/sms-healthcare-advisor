"""
SMS Service Integration for Healthcare Advisor
Supports Twilio and other SMS providers
"""
import os
from typing import Optional, Dict
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse


class SMSService:
    """
    SMS service wrapper for sending and receiving SMS messages.
    Currently supports Twilio.
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        """
        Initialize SMS service.
        
        Args:
            account_sid: Twilio Account SID (or set TWILIO_ACCOUNT_SID env var)
            auth_token: Twilio Auth Token (or set TWILIO_AUTH_TOKEN env var)
            from_number: Twilio phone number to send from (or set TWILIO_FROM_NUMBER env var)
        """
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_FROM_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError(
                "Missing Twilio credentials. Provide account_sid, auth_token, and from_number "
                "or set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER environment variables."
            )
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        """
        Send an SMS message.
        
        Args:
            to_number: Recipient phone number (E.164 format, e.g., +1234567890)
            message: Message content
            
        Returns:
            Dictionary with message details and status
        """
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status,
                "to": message_obj.to,
                "from": message_obj.from_,
                "body": message_obj.body
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_response(self, message: str) -> str:
        """
        Create a TwiML response for incoming SMS webhooks.
        
        Args:
            message: Response message to send
            
        Returns:
            TwiML XML string
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def validate_webhook(self, request_signature: str, url: str, params: Dict) -> bool:
        """
        Validate incoming webhook request from Twilio.
        
        Args:
            request_signature: X-Twilio-Signature header value
            url: Full URL of the webhook endpoint
            params: Request parameters
            
        Returns:
            True if valid, False otherwise
        """
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(self.auth_token)
            return validator.validate(url, params, request_signature)
        except Exception:
            return False

