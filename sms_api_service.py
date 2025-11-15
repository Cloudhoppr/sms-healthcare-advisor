"""
API-based SMS Service for Healthcare Advisor
Polls for incoming messages and sends responses via API (no webhooks required)
"""
import os
import time
from typing import List, Dict, Optional
from twilio.rest import Client
from llm_model import HealthcareAdvisor


class SMSAPIService:
    """
    API-based SMS service that polls for messages and processes them.
    No webhook configuration needed.
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
        advisor: Optional[HealthcareAdvisor] = None
    ):
        """
        Initialize API-based SMS service.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_number: Twilio phone number to send from
            advisor: HealthcareAdvisor instance (creates new if None)
        """
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = from_number or os.getenv("TWILIO_FROM_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError(
                "Missing Twilio credentials. Set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER environment variables."
            )
        
        self.client = Client(self.account_sid, self.auth_token)
        self.advisor = advisor or HealthcareAdvisor()
        
        # Track processed message SIDs to avoid duplicates
        self.processed_messages = set()
    
    def get_incoming_messages(
        self,
        limit: int = 10,
        since: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch incoming messages from Twilio API.
        
        Args:
            limit: Maximum number of messages to fetch
            since: ISO date string to fetch messages since (e.g., "2025-11-15T20:00:00Z")
            
        Returns:
            List of message dictionaries
        """
        try:
            messages = self.client.messages.list(
                to=self.from_number,
                limit=limit
            )
            
            result = []
            for msg in messages:
                if msg.direction == "inbound":
                    message_data = {
                        "sid": msg.sid,
                        "from": msg.from_,
                        "to": msg.to,
                        "body": msg.body,
                        "date_sent": str(msg.date_sent) if msg.date_sent else None,
                        "date_created": str(msg.date_created),
                        "status": msg.status
                    }
                    result.append(message_data)
            
            return result
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []
    
    def process_new_messages(self, context_per_number: Optional[Dict[str, list]] = None) -> List[Dict]:
        """
        Process new incoming messages and send responses.
        
        Args:
            context_per_number: Dictionary mapping phone numbers to conversation contexts
            
        Returns:
            List of processing results
        """
        if context_per_number is None:
            context_per_number = {}
        
        # Get incoming messages
        messages = self.get_incoming_messages(limit=20)
        
        results = []
        for msg in messages:
            msg_sid = msg["sid"]
            from_number = msg["from"]
            
            # Skip if already processed
            if msg_sid in self.processed_messages:
                continue
            
            # Get conversation context for this number
            if from_number not in context_per_number:
                context_per_number[from_number] = []
            
            context = context_per_number[from_number]
            
            # Process with healthcare advisor
            try:
                response_text = self.advisor.get_advice(msg["body"], context=context)
                
                # Update context
                context.append(msg["body"])
                context.append(response_text)
                
                # Keep context manageable
                if len(context) > 10:
                    context_per_number[from_number] = context[-10:]
                
                # Send response
                send_result = self.send_sms(from_number, response_text)
                
                results.append({
                    "message_sid": msg_sid,
                    "from": from_number,
                    "original_message": msg["body"],
                    "response_sent": send_result["success"],
                    "response_sid": send_result.get("message_sid"),
                    "error": send_result.get("error")
                })
                
                # Mark as processed
                self.processed_messages.add(msg_sid)
                
            except Exception as e:
                results.append({
                    "message_sid": msg_sid,
                    "from": from_number,
                    "error": str(e),
                    "response_sent": False
                })
                self.processed_messages.add(msg_sid)
        
        return results
    
    def send_sms(self, to_number: str, message: str) -> Dict:
        """
        Send an SMS message via API.
        
        Args:
            to_number: Recipient phone number
            message: Message content
            
        Returns:
            Dictionary with send result
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
                "from": message_obj.from_
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_polling(
        self,
        interval: int = 10,
        callback: Optional[callable] = None
    ):
        """
        Start polling for new messages continuously.
        
        Args:
            interval: Seconds between polls
            callback: Optional callback function to call with results
        """
        print(f"Starting SMS polling service (checking every {interval} seconds)...")
        print(f"Press Ctrl+C to stop\n")
        
        context_per_number = {}
        
        try:
            while True:
                results = self.process_new_messages(context_per_number)
                
                if results:
                    print(f"Processed {len(results)} new message(s)")
                    for result in results:
                        if result["response_sent"]:
                            print(f"  ✓ Responded to {result['from']}")
                        else:
                            print(f"  ✗ Failed to respond to {result['from']}: {result.get('error')}")
                
                if callback:
                    callback(results)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nPolling stopped.")


if __name__ == "__main__":
    # Example usage
    service = SMSAPIService()
    
    # Process messages once
    print("Processing new messages...")
    results = service.process_new_messages()
    
    if results:
        print(f"\nProcessed {len(results)} message(s):")
        for result in results:
            print(f"  From: {result['from']}")
            print(f"  Response sent: {result['response_sent']}")
    else:
        print("No new messages to process.")
    
    # Uncomment to start continuous polling:
    # service.start_polling(interval=10)

