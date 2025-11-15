# SMS Healthcare Advisor

An AI-powered healthcare advisor that provides medical advice via SMS using Hugging Face language models. The system uses conversational AI to understand symptoms, provide health information, and guide users on next steps.

## Features

- 🤖 **Hugging Face LLM Integration**: Uses state-of-the-art language models for natural healthcare conversations
- 📱 **SMS Integration**: Receive and respond to healthcare questions via SMS using Twilio
- 🧠 **Symptom Analysis**: Intelligent symptom extraction and condition matching
- 📚 **Knowledge Base**: Built-in knowledge base for common conditions (cold, flu, headaches, sleep issues, allergies, stomach flu)
- 💬 **Conversation Context**: Maintains conversation history for better diagnosis
- 🔒 **Webhook Validation**: Secure webhook handling for SMS messages

## Architecture

- **`llm_model.py`**: Core healthcare advisor with LLM integration and knowledge base
- **`sms_service.py`**: SMS service wrapper for Twilio integration
- **`sms_server.py`**: Flask web server for handling SMS webhooks and API endpoints

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sms-healthcare-advisor
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Twilio Setup

1. Sign up for a [Twilio account](https://www.twilio.com/try-twilio)
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a phone number or use a trial number
4. Set environment variables:

```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_FROM_NUMBER="+1234567890"
```

Or create a `.env` file (you'll need `python-dotenv` package):
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
HF_MODEL_NAME=microsoft/DialoGPT-medium
PORT=5000
FLASK_DEBUG=False
```

### Hugging Face Model

The default model is `microsoft/DialoGPT-medium`. You can change it by setting the `HF_MODEL_NAME` environment variable or modifying the code.

## Usage

### Running the SMS Server

Start the Flask server:

```bash
python sms_server.py
```

The server will start on `http://localhost:5000` (or the port specified in `PORT`).

### Endpoints

- **`GET /`**: Health check endpoint
- **`POST /sms/webhook`**: Twilio webhook endpoint for incoming SMS messages
- **`POST /sms/send`**: API endpoint to send SMS messages
- **`POST /sms/test`**: Test endpoint to interact with the advisor without SMS

### Testing the Advisor (Without SMS)

You can test the healthcare advisor directly:

```bash
python llm_model.py
```

Or use the test endpoint:

```bash
curl -X POST http://localhost:5000/sms/test \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache and feel tired"}'
```

### Sending SMS via API

```bash
curl -X POST http://localhost:5000/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "Hello! How can I help with your health question?"
  }'
```

### Setting Up Twilio Webhook

1. In your Twilio Console, go to your phone number settings
2. Set the webhook URL to: `https://your-domain.com/sms/webhook`
3. Set HTTP method to `POST`
4. Save the configuration

For local development, use a tool like [ngrok](https://ngrok.com/) to expose your local server:

```bash
ngrok http 5000
```

Then use the ngrok URL in your Twilio webhook configuration.

## How It Works

1. **Incoming SMS**: When a user sends an SMS to your Twilio number, Twilio sends a webhook to `/sms/webhook`
2. **Message Processing**: The server extracts the message and phone number
3. **Context Retrieval**: Retrieves conversation history for that phone number
4. **Advisor Processing**: The Healthcare Advisor:
   - Checks the knowledge base for direct matches
   - Extracts symptoms from the message
   - Matches symptoms to conditions
   - Generates a response using the LLM
5. **Response**: Sends the response back via SMS using Twilio

## Knowledge Base

The advisor includes a knowledge base for common conditions:

- **Cold**: Symptoms, description, and next steps
- **Flu**: Influenza symptoms and recommendations
- **Headache**: Relief methods and when to see a doctor
- **Sleep Issues**: Sleep hygiene tips
- **Allergies**: Common allergy symptoms and management
- **Stomach Flu**: Gastroenteritis symptoms and care

## Conversation Flow

The advisor maintains conversation context per phone number, allowing for multi-turn conversations:

1. User: "I have a headache"
2. Advisor: "I've noted your symptoms: headache. To help provide a better assessment..."
3. User: "It's been going on for 2 days and I feel nauseous"
4. Advisor: Provides diagnosis and next steps based on multiple symptoms

## Important Medical Disclaimer

⚠️ **This is not a medical diagnosis tool.** The healthcare advisor provides general health information and should not replace professional medical advice. Users should always consult with healthcare professionals for proper evaluation and treatment, especially for:
- Severe symptoms
- Worsening conditions
- Persistent symptoms
- Emergency situations

## Development

### Project Structure

```
sms-healthcare-advisor/
├── llm_model.py          # Core healthcare advisor and LLM integration
├── sms_service.py        # SMS service wrapper (Twilio)
├── sms_server.py         # Flask web server for SMS webhooks
├── config.example.py     # Example configuration
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
└── README.md            # This file
```

### Requirements

- Python 3.11+
- PyTorch (for model inference)
- Transformers (Hugging Face)
- Flask (web server)
- Twilio (SMS service)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

