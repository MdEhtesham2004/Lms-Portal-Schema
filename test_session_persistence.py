"""
Test script to verify Redis session configuration
Run this after starting your Flask app to test session persistence
"""
import requests

BASE_URL = "http://localhost:5000/api/v1"

def test_session_persistence():
    print("Testing session persistence between /register and /verify-otp...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Register (this should store data in session)
    register_data = {
        "email": "test@example.com",
        "password": "Test@123456",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890"
    }
    
    print("\n1. Calling /register endpoint...")
    response = session.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   Cookies: {session.cookies.get_dict()}")
    
    # Step 2: Verify OTP (this should access session data)
    print("\n2. Calling /verify-otp endpoint with same session...")
    verify_data = {
        "otp": "123456"  # Replace with actual OTP from Twilio
    }
    
    response = session.post(f"{BASE_URL}/auth/verify-otp", json=verify_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Check if session data was accessible
    if "Session expired" in response.text:
        print("\n❌ FAILED: Session data was not accessible")
        print("   This means the session is not persisting between requests")
    else:
        print("\n✅ SUCCESS: Session data is accessible")
        print("   (Note: OTP verification may still fail if OTP is invalid)")

if __name__ == "__main__":
    test_session_persistence()
