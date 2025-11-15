# SMS Healthcare Advisor - API Documentation

## Overview

This is an **API-based architecture** that doesn't require webhooks. Messages are fetched via API polling and responses are sent via API calls.

## Architecture

- **No webhooks required** - Uses API polling instead
- **RESTful API** - Standard HTTP endpoints
- **Stateless processing** - Process messages on-demand
- **Flexible** - Can be integrated into any system

## API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Health Check
```
GET /
```
Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "SMS Healthcare Advisor API",
  "advisor_initialized": true,
  "api_service_initialized": true
}
```

### 2. Get Incoming Messages
```
GET /api/v1/messages/incoming?limit=10
```
Fetch incoming SMS messages from Twilio.

**Query Parameters:**
- `limit` (optional): Number of messages to fetch (default: 10)

**Response:**
```json
{
  "success": true,
  "count": 2,
  "messages": [
    {
      "sid": "SM123...",
      "from": "+1234567890",
      "to": "+18573552130",
      "body": "I have a headache",
      "date_sent": "2025-11-15T20:00:00Z",
      "status": "received"
    }
  ]
}
```

### 3. Process Messages (Auto-Respond)
```
POST /api/v1/messages/process
```
Fetches new incoming messages, processes them through the Healthcare Advisor, and automatically sends responses.

**Response:**
```json
{
  "success": true,
  "processed": 1,
  "results": [
    {
      "message_sid": "SM123...",
      "from": "+1234567890",
      "original_message": "I have a headache",
      "response_sent": true,
      "response_sid": "SM456...",
      "error": null
    }
  ]
}
```

### 4. Send SMS Message
```
POST /api/v1/messages/send
```
Send an SMS message.

**Request Body:**
```json
{
  "to": "+1234567890",
  "message": "Your message here"
}
```

**Response:**
```json
{
  "success": true,
  "message_sid": "SM789...",
  "status": "queued",
  "to": "+1234567890",
  "from": "+18573552130"
}
```

### 5. Get Healthcare Advice (No SMS)
```
POST /api/v1/advisor/advice
```
Get healthcare advice without sending SMS. Useful for testing or web integration.

**Request Body:**
```json
{
  "message": "I have a headache",
  "phone_number": "+1234567890"  // optional, for context
}
```

**Response:**
```json
{
  "success": true,
  "response": "I've noted your symptoms: headache...",
  "phone_number": "+1234567890"
}
```

### 6. Service Status
```
GET /api/v1/status
```
Get service status and statistics.

**Response:**
```json
{
  "advisor_initialized": true,
  "api_service_initialized": true,
  "active_conversations": 2,
  "conversation_contexts": {
    "+1234567890": 4,
    "+0987654321": 2
  },
  "recent_incoming_messages": 5
}
```

## Usage Examples

### Python
```python
import requests

# Process new messages and auto-respond
response = requests.post("http://localhost:5000/api/v1/messages/process")
print(response.json())

# Get incoming messages
response = requests.get("http://localhost:5000/api/v1/messages/incoming?limit=10")
print(response.json())

# Send a message
response = requests.post(
    "http://localhost:5000/api/v1/messages/send",
    json={"to": "+1234567890", "message": "Hello!"}
)
print(response.json())

# Get advice without SMS
response = requests.post(
    "http://localhost:5000/api/v1/advisor/advice",
    json={"message": "I have a headache"}
)
print(response.json())
```

### cURL
```bash
# Process messages
curl -X POST http://localhost:5000/api/v1/messages/process

# Get incoming messages
curl http://localhost:5000/api/v1/messages/incoming?limit=10

# Send SMS
curl -X POST http://localhost:5000/api/v1/messages/send \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890", "message": "Hello!"}'

# Get advice
curl -X POST http://localhost:5000/api/v1/advisor/advice \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a headache"}'
```

### JavaScript/Node.js
```javascript
// Process messages
fetch('http://localhost:5000/api/v1/messages/process', {
  method: 'POST'
})
.then(res => res.json())
.then(data => console.log(data));

// Get incoming messages
fetch('http://localhost:5000/api/v1/messages/incoming?limit=10')
.then(res => res.json())
.then(data => console.log(data));

// Send SMS
fetch('http://localhost:5000/api/v1/messages/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    to: '+1234567890',
    message: 'Hello!'
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## Polling Strategy

Since this architecture doesn't use webhooks, you need to poll for new messages:

### Option 1: Manual Polling
Call `/api/v1/messages/process` periodically (e.g., every 10-30 seconds).

### Option 2: Automated Polling Script
Use the `SMSAPIService` class directly:

```python
from sms_api_service import SMSAPIService

service = SMSAPIService()
service.start_polling(interval=10)  # Check every 10 seconds
```

### Option 3: Cron Job / Scheduled Task
Set up a cron job or scheduled task to call the API endpoint:

```bash
# Every 30 seconds
*/30 * * * * curl -X POST http://localhost:5000/api/v1/messages/process
```

## Integration Examples

### Web Application
```python
# In your web app, periodically check for new messages
import requests
import time

def check_messages():
    response = requests.post("http://localhost:5000/api/v1/messages/process")
    return response.json()

# Run in background thread
while True:
    check_messages()
    time.sleep(30)  # Check every 30 seconds
```

### Microservices
Each service can call the API independently:
- Frontend calls `/api/v1/advisor/advice` for chat interface
- Background worker calls `/api/v1/messages/process` for SMS processing
- Admin panel calls `/api/v1/messages/incoming` to view messages

## Advantages of API Architecture

1. **No webhook configuration** - Works behind firewalls, no public URL needed
2. **Flexible integration** - Can be called from any system
3. **Better control** - Process messages on your schedule
4. **Easier debugging** - See exactly when and how messages are processed
5. **Scalable** - Can handle multiple instances, load balancing

## Configuration

Set environment variables:
```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_FROM_NUMBER="+18573552130"
export PORT=5000
export FLASK_DEBUG=False
```

## Running the Server

```bash
python api_server.py
```

The server will start on port 5000 (or PORT environment variable).

