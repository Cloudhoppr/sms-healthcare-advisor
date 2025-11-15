# How to Send SMS from Twilio Console

## Quick Steps:

1. **Go to Twilio Console:**
   - Visit: https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms
   - Or navigate: Twilio Console → Develop → Messaging → Try it out → Send an SMS

2. **Fill in the form:**
   - **From:** Select your Twilio number: `+18573552130`
   - **To:** Enter the recipient: `+18048470893`
   - **Message:** Type your test message

3. **Click "Send Message"**

4. **Check the result:**
   - Success = Message sent (check your phone)
   - Failure = See error message for details

## Alternative Method:

You can also send from the Phone Numbers page:

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/active
2. Click on your number `+18573552130`
3. Scroll to "Messaging" section
4. Use the "Send a test SMS" feature

## What to Look For:

- **If it works from Console:** The issue is in our code
- **If it fails from Console:** The issue is with:
  - Phone number (landline, can't receive SMS)
  - Carrier blocking
  - Account restrictions
  - Number format

## Check Message Logs:

After sending, check logs at:
https://console.twilio.com/us1/monitor/logs/sms

This shows detailed status and error information for each message.

