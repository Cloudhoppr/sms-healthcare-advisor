@echo off
REM Twilio Configuration Script for Windows CMD
REM Run this script to set up your Twilio environment variables

REM Set your Twilio credentials here
REM set TWILIO_ACCOUNT_SID=your_account_sid_here
REM set TWILIO_AUTH_TOKEN=your_auth_token_here
REM set TWILIO_FROM_NUMBER=+1234567890

echo Twilio Configuration Complete!
echo   Account SID: %TWILIO_ACCOUNT_SID%
echo   Auth Token: %TWILIO_AUTH_TOKEN%
echo   From Number: %TWILIO_FROM_NUMBER%
echo.
echo All Twilio credentials are configured!
echo You can now run: python sms_server.py

