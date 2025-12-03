"""
Test script to verify Flask rate limiting with Redis
"""
import requests
import time

# Configuration
BASE_URL = "http://localhost:5000"
ENDPOINT = "/api/v1/public/get-courses"
RATE_LIMIT = 30  # 30 per minute for this endpoint

def test_rate_limiting():
    print("🧪 Testing Rate Limiting with Redis\n")
    print(f"Endpoint: {BASE_URL}{ENDPOINT}")
    print(f"Expected Rate Limit: {RATE_LIMIT} per minute\n")
    
    success_count = 0
    blocked_count = 0
    
    # Make MORE requests to ensure we hit the limit
    for i in range(1, RATE_LIMIT + 10):
        try:
            response = requests.post(f"{BASE_URL}{ENDPOINT}")
            
            # Check rate limit headers
            limit = response.headers.get('X-RateLimit-Limit', 'N/A')
            remaining = response.headers.get('X-RateLimit-Remaining', 'N/A')
            reset = response.headers.get('X-RateLimit-Reset', 'N/A')
            
            if response.status_code == 200:
                success_count += 1
                if i <= 5 or i >= RATE_LIMIT - 2:  # Show first 5 and last few
                    print(f"✅ Request {i:2d}: SUCCESS | Limit: {limit} | Remaining: {remaining}")
                elif i == 6:
                    print(f"   ... (showing first 5 and last few)")
            elif response.status_code == 429:
                blocked_count += 1
                retry_after = response.headers.get('Retry-After', 'N/A')
                print(f"❌ Request {i:2d}: RATE LIMITED | Retry after: {retry_after}s")
                if blocked_count == 1:
                    print(f"\n🎯 Rate limit triggered after {success_count} successful requests!")
                    print(f"   This is {'CORRECT' if success_count == RATE_LIMIT else 'UNEXPECTED'}!")
                    print(f"   Expected: {RATE_LIMIT}, Got: {success_count}\n")
            else:
                print(f"⚠️  Request {i:2d}: Unexpected status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: Cannot connect to Flask app.")
            print("   Make sure the app is running: python main.py")
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results:")
    print(f"{'='*60}")
    print(f"   Successful requests: {success_count}")
    print(f"   Blocked requests: {blocked_count}")
    print(f"   Expected limit: {RATE_LIMIT}")
    
    if blocked_count > 0:
        if success_count == RATE_LIMIT:
            print(f"\n✅ PASS: Rate limiting is working CORRECTLY!")
            print(f"   ✓ Exactly {RATE_LIMIT} requests allowed")
            print(f"   ✓ Subsequent requests blocked")
            print(f"   ✓ Storage: Redis (data persists across restarts)")
        else:
            print(f"\n⚠️  WARNING: Rate limiting is active but limit seems off")
            print(f"   Expected {RATE_LIMIT} requests, got {success_count}")
    else:
        print(f"\n❌ FAIL: Rate limiting is NOT working!")
        print(f"   All {success_count} requests succeeded (expected max {RATE_LIMIT})")
        print(f"\n🔍 Troubleshooting:")
        print(f"   1. Check Flask app logs for: '✅ Rate limiting ENABLED'")
        print(f"   2. Verify RATELIMIT_ENABLED=true in .env")
        print(f"   3. Check if Redis is running: redis-cli PING")
        print(f"   4. Restart Flask app after making changes")

if __name__ == "__main__":
    test_rate_limiting()

