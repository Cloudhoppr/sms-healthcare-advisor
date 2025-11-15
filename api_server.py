"""
REST API Server for SMS Healthcare Advisor
API-based architecture - no webhooks required
"""
import os
from flask import Flask, request, jsonify
from typing import Dict, Optional
from sms_api_service import SMSAPIService
from llm_model import HealthcareAdvisor

app = Flask(__name__)

# Initialize services
api_service: Optional[SMSAPIService] = None
advisor: Optional[HealthcareAdvisor] = None

# Store conversation contexts per phone number
conversation_contexts: Dict[str, list] = {}


def initialize_services():
    """Initialize the API service and advisor."""
    global api_service, advisor
    
    if advisor is None:
        print("Initializing Healthcare Advisor...")
        model_name = os.getenv("HF_MODEL_NAME", "microsoft/DialoGPT-medium")
        advisor = HealthcareAdvisor(model_name=model_name)
        print("Healthcare Advisor initialized.")
    
    if api_service is None:
        print("Initializing SMS API Service...")
        try:
            api_service = SMSAPIService(advisor=advisor)
            print("SMS API Service initialized.")
        except ValueError as e:
            print(f"Warning: SMS API Service not initialized: {e}")
            return False
    
    return True


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    initialize_services()
    return jsonify({
        "status": "healthy",
        "service": "SMS Healthcare Advisor API",
        "advisor_initialized": advisor is not None,
        "api_service_initialized": api_service is not None
    }), 200


@app.route("/api/v1/messages/incoming", methods=["GET"])
def get_incoming_messages():
    """
    Get incoming messages from Twilio.
    
    Query parameters:
    - limit: Number of messages to fetch (default: 10)
    """
    initialize_services()
    
    if not api_service:
        return jsonify({"error": "SMS API Service not initialized"}), 500
    
    limit = request.args.get("limit", 10, type=int)
    
    try:
        messages = api_service.get_incoming_messages(limit=limit)
        return jsonify({
            "success": True,
            "count": len(messages),
            "messages": messages
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/messages/process", methods=["POST"])
def process_messages():
    """
    Process new incoming messages and send responses.
    
    This endpoint:
    1. Fetches new incoming messages
    2. Processes them through the Healthcare Advisor
    3. Sends responses automatically
    
    Returns list of processed messages.
    """
    initialize_services()
    
    if not api_service:
        return jsonify({"error": "SMS API Service not initialized"}), 500
    
    try:
        results = api_service.process_new_messages(conversation_contexts)
        return jsonify({
            "success": True,
            "processed": len(results),
            "results": results
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/messages/send", methods=["POST"])
def send_message():
    """
    Send an SMS message.
    
    JSON body:
    {
        "to": "+1234567890",
        "message": "Your message here"
    }
    """
    initialize_services()
    
    if not api_service:
        return jsonify({"error": "SMS API Service not initialized"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    to_number = data.get("to")
    message = data.get("message")
    
    if not to_number or not message:
        return jsonify({"error": "Missing 'to' or 'message' in request"}), 400
    
    result = api_service.send_sms(to_number, message)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route("/api/v1/advisor/advice", methods=["POST"])
def get_advice():
    """
    Get healthcare advice for a message (without SMS).
    
    JSON body:
    {
        "message": "I have a headache",
        "phone_number": "+1234567890"  # optional, for context
    }
    """
    initialize_services()
    
    if not advisor:
        return jsonify({"error": "Healthcare Advisor not initialized"}), 500
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    message_body = data.get("message", "").strip()
    phone_number = data.get("phone_number", "api_user")
    
    if not message_body:
        return jsonify({"error": "Missing 'message' in request"}), 400
    
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
        
        return jsonify({
            "success": True,
            "response": response_text,
            "phone_number": phone_number
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/v1/status", methods=["GET"])
def get_status():
    """Get service status and statistics."""
    initialize_services()
    
    status = {
        "advisor_initialized": advisor is not None,
        "api_service_initialized": api_service is not None,
        "active_conversations": len(conversation_contexts),
        "conversation_contexts": {
            phone: len(context) for phone, context in conversation_contexts.items()
        }
    }
    
    if api_service:
        try:
            recent_messages = api_service.get_incoming_messages(limit=5)
            status["recent_incoming_messages"] = len(recent_messages)
        except:
            pass
    
    return jsonify(status), 200


if __name__ == "__main__":
    # Initialize services on startup
    initialize_services()
    
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    print(f"\n{'='*70}")
    print("SMS Healthcare Advisor - API Server")
    print(f"{'='*70}")
    print(f"Server starting on port {port}")
    print(f"Debug mode: {debug}")
    print(f"\nAPI Endpoints:")
    print(f"  GET  /                           - Health check")
    print(f"  GET  /api/v1/messages/incoming   - Get incoming messages")
    print(f"  POST /api/v1/messages/process    - Process new messages & respond")
    print(f"  POST /api/v1/messages/send      - Send SMS message")
    print(f"  POST /api/v1/advisor/advice      - Get advice (no SMS)")
    print(f"  GET  /api/v1/status               - Service status")
    print(f"\n{'='*70}\n")
    
    app.run(host="0.0.0.0", port=port, debug=debug)

