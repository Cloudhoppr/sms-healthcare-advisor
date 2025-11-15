# Setting Up Twilio Webhook for SMS Healthcare Advisor

## What You Need:
1. Your server running (or a public URL)
2. Twilio account with phone number

## Steps:

### Option 1: Local Development with ngrok

1. **Install ngrok:**
   - Download from: https://ngrok.com/download
   - Or: `choco install ngrok` (if you have Chocolatey)

2. **Start your server:**
   ```powershell
   python sms_server.py
   ```

3. **In a new terminal, start ngrok:**
   ```powershell
   ngrok http 5000
   ```

4. **Copy the ngrok URL** (looks like: `https://abc123.ngrok.io`)

5. **Configure Twilio Webhook:**
   - Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
   - Click on your number: `+18573552130`
   - Scroll to "Messaging" section
   - Under "A MESSAGE COMES IN", enter:
     ```
     https://your-ngrok-url.ngrok.io/sms/webhook
     ```
   - Set HTTP method to: `POST`
   - Click "Save"

### Option 2: Production (with public server)

1. Deploy your server to a public URL (e.g., Heroku, AWS, etc.)

2. Configure webhook:
   - Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
   - Click on your number: `+18573552130`
   - Under "A MESSAGE COMES IN", enter:
     ```
     https://your-domain.com/sms/webhook
     ```
   - Set HTTP method to: `POST`
   - Click "Save"

## Testing:

Once webhook is configured:
1. Send an SMS to `+18573552130` from any phone
2. The Healthcare Advisor will automatically respond!

## Quick Test Without Webhook:

You can test the advisor locally using:
```powershell
curl -X POST http://localhost:5000/sms/test -H "Content-Type: application/json" -d "{\"message\": \"I have a headache\"}"
```

Or use the test endpoint in your browser/Postman.

