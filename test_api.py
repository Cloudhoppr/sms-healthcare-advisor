"""Test the new API endpoints"""
import requests
import json

base_url = "http://localhost:5000"

print("Testing SMS Healthcare Advisor API\n")
print("=" * 70)

# Test 1: Health Check
print("\n1. Health Check")
try:
    response = requests.get(f"{base_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Get Incoming Messages
print("\n2. Get Incoming Messages")
try:
    response = requests.get(f"{base_url}/api/v1/messages/incoming?limit=5")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Messages found: {data.get('count', 0)}")
    if data.get('messages'):
        for msg in data['messages'][:2]:
            print(f"   - From {msg['from']}: {msg['body'][:50]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Process Messages
print("\n3. Process New Messages (Auto-Respond)")
try:
    response = requests.post(f"{base_url}/api/v1/messages/process")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Processed: {data.get('processed', 0)} message(s)")
    if data.get('results'):
        for result in data['results']:
            status = "SUCCESS" if result.get('response_sent') else "FAILED"
            print(f"   - {status}: {result.get('from')} - {result.get('original_message', '')[:30]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Get Advice (No SMS)
print("\n4. Get Healthcare Advice (No SMS)")
try:
    response = requests.post(
        f"{base_url}/api/v1/advisor/advice",
        json={"message": "I have a headache and feel tired"}
    )
    data = response.json()
    print(f"   Status: {response.status_code}")
    if data.get('success'):
        print(f"   Response: {data.get('response', '')[:100]}...")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Service Status
print("\n5. Service Status")
try:
    response = requests.get(f"{base_url}/api/v1/status")
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Advisor initialized: {data.get('advisor_initialized')}")
    print(f"   API service initialized: {data.get('api_service_initialized')}")
    print(f"   Active conversations: {data.get('active_conversations', 0)}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("API Testing Complete!")

