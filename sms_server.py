"""
Flask web server for handling SMS webhooks and serving the Healthcare Advisor
"""
import os
from flask import Flask, request, Response
from typing import Dict, Optional
from llm_model import HealthcareAdvisor
from sms_service import SMSService

app = Flask(__name__)

# Initialize services
advisor: Optional[HealthcareAdvisor] = None
sms_service: Optional[SMSService] = None

# Store conversation contexts per phone number
conversation_contexts: Dict[str, list] = {}


def initialize_services():
    """Initialize the healthcare advisor and SMS service."""
    global advisor, sms_service
    
    if advisor is None:
        print("Initializing Healthcare Advisor...")
        model_name = os.getenv("HF_MODEL_NAME", "microsoft/DialoGPT-medium")
        advisor = HealthcareAdvisor(model_name=model_name)
        print("Healthcare Advisor initialized.")
    
    if sms_service is None:
        print("Initializing SMS Service...")
        try:
            sms_service = SMSService()
            print("SMS Service initialized.")
        except ValueError as e:
            print(f"Warning: SMS Service not initialized: {e}")
            print("SMS sending will be disabled. Webhook receiving will still work.")


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SMS Healthcare Advisor",
        "advisor_initialized": advisor is not None,
        "sms_service_initialized": sms_service is not None
    }, 200


@app.route("/sms/webhook", methods=["POST"])
def sms_webhook():
    """
    Handle incoming SMS webhook from Twilio.
    
    Expected environment variables:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_FROM_NUMBER
    """
    # Initialize services if not already done
    initialize_services()
    
    # Get incoming message details
    from_number = request.form.get("From", "")
    to_number = request.form.get("To", "")
    message_body = request.form.get("Body", "").strip()
    
    # Validate webhook (optional but recommended)
    if sms_service:
        signature = request.headers.get("X-Twilio-Signature", "")
        url = request.url
        params = request.form.to_dict()
        
        # Uncomment to enable webhook validation
        # if not sms_service.validate_webhook(signature, url, params):
        #     return Response("Invalid signature", status=403)
    
    if not message_body:
        return sms_service.create_response("Please send a message with your health question.") if sms_service else ""
    
    # Get or create conversation context for this phone number
    if from_number not in conversation_contexts:
        conversation_contexts[from_number] = []
    
    context = conversation_contexts[from_number]
    
    # Process the message through the healthcare advisor
    try:
        response_text = advisor.get_advice(message_body, context=context)
        
        # Update context with the exchange
        context.append(message_body)
        context.append(response_text)
        
        # Keep context manageable (last 10 messages)
        if len(context) > 10:
            conversation_contexts[from_number] = context[-10:]
        
    except Exception as e:
        print(f"Error processing message: {e}")
        response_text = (
            "I apologize, but I encountered an error processing your message. "
            "Please try again or consult a healthcare professional for immediate assistance."
        )
    
    # Create and return TwiML response
    if sms_service:
        return sms_service.create_response(response_text)
    else:
        # Fallback if SMS service not initialized (for testing)
        return Response(response_text, mimetype="text/plain")


@app.route("/sms/send", methods=["POST"])
def send_sms():
    """
    Send an SMS message via API.
    
    Expected JSON body:
    {
        "to": "+1234567890",
        "message": "Your message here"
    }
    """
    initialize_services()
    
    if not sms_service:
        return {"error": "SMS service not initialized"}, 500
    
    data = request.get_json()
    if not data:
        return {"error": "No JSON data provided"}, 400
    
    to_number = data.get("to")
    message = data.get("message")
    
    if not to_number or not message:
        return {"error": "Missing 'to' or 'message' in request"}, 400
    
    result = sms_service.send_sms(to_number, message)
    
    if result["success"]:
        return result, 200
    else:
        return result, 500


@app.route("/sms/test", methods=["POST"])
def test_sms():
    """
    Test endpoint that processes a message without sending SMS.
    Useful for testing the advisor without Twilio setup.
    
    Expected JSON body:
    {
        "message": "I have a headache",
        "phone_number": "+1234567890"  # optional, for context tracking
    }
    """
    initialize_services()
    
    data = request.get_json()
    if not data:
        return {"error": "No JSON data provided"}, 400
    
    message_body = data.get("message", "").strip()
    phone_number = data.get("phone_number", "test_user")
    
    if not message_body:
        return {"error": "Missing 'message' in request"}, 400
    
    # Get or create conversation context
    if phone_number not in conversation_contexts:
        conversation_contexts[phone_number] = []
    
    context = conversation_contexts[phone_number]
    
    try:
        response_text = advisor.get_advice(message_body, context=context)
        
        # Update context
        context.append(message_body)
        context.append(response_text)
        
        if len(context) > 10:
            conversation_contexts[phone_number] = context[-10:]
        
        return {
            "success": True,
            "response": response_text,
            "phone_number": phone_number
        }, 200
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 500


if __name__ == "__main__":
    # Initialize services on startup
    initialize_services()
    
    # Get port from environment or default to 5000
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    print(f"\n{'='*70}")
    print("SMS Healthcare Advisor Server")
    print(f"{'='*70}")
    print(f"Server starting on port {port}")
    print(f"Debug mode: {debug}")
    print(f"\nEndpoints:")
    print(f"  - Health check: http://localhost:{port}/")
    print(f"  - SMS webhook: http://localhost:{port}/sms/webhook")
    print(f"  - Send SMS: http://localhost:{port}/sms/send (POST)")
    print(f"  - Test advisor: http://localhost:{port}/sms/test (POST)")
    print(f"\n{'='*70}\n")
    
    app.run(host="0.0.0.0", port=port, debug=debug)

