import firebase_admin
from firebase_admin import auth, credentials
import requests
import json
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Initialize Firebase Admin
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
})

try:
    firebase_admin.initialize_app(cred)
except ValueError:
    # App already initialized
    pass

# Test user data
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def create_test_user():
    try:
        # Create a test user
        user = auth.create_user(
            email=TEST_EMAIL,
            password=TEST_PASSWORD
        )
        print(f"Created test user with UID: {user.uid}")
        return user.uid
    except auth.EmailAlreadyExistsError:
        # If user exists, get their UID
        user = auth.get_user_by_email(TEST_EMAIL)
        print(f"User already exists with UID: {user.uid}")
        return user.uid

def get_id_token():
    # Sign in with email and password to get ID token
    response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('FIREBASE_WEB_API_KEY')}",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "returnSecureToken": True
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token response: {json.dumps(token_data, indent=2)}")
        return token_data["idToken"]
    else:
        print(f"Error response: {response.text}")
        raise Exception(f"Failed to get ID token: {response.text}")

def test_endpoints(id_token):
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }
    
    # Test user creation
    print("\n1. Testing user creation...")
    user_data = {
        "email": TEST_EMAIL,
        "firebase_uid": auth.get_user_by_email(TEST_EMAIL).uid
    }
    print(f"Request headers: {json.dumps(headers, indent=2)}")
    print(f"Request data: {json.dumps(user_data, indent=2)}")
    response = requests.post(f"{base_url}/users", headers=headers, json=user_data)
    print(f"User creation response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    if response.status_code != 200:
        print("Skipping remaining tests due to authentication failure")
        return
    
    # Test getting current user
    print("\n2. Testing get current user...")
    response = requests.get(f"{base_url}/me", headers=headers)
    print(f"Get current user response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Test adding to watchlist
    print("\n3. Testing add to watchlist...")
    watchlist_data = {"ticker": "AAPL"}
    response = requests.post(f"{base_url}/watchlist", headers=headers, json=watchlist_data)
    print(f"Add to watchlist response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Test getting watchlist
    print("\n4. Testing get watchlist...")
    response = requests.get(f"{base_url}/watchlist", headers=headers)
    print(f"Get watchlist response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Test saving summary
    print("\n5. Testing save summary...")
    summary_data = {
        "ticker": "AAPL",
        "summary_text": "Strong Q4 earnings with revenue growth of 20%..."
    }
    response = requests.post(f"{base_url}/summaries", headers=headers, json=summary_data)
    print(f"Save summary response: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Test getting summaries
    print("\n6. Testing get summaries...")
    response = requests.get(f"{base_url}/summaries", headers=headers)
    print(f"Get summaries response: {response.status_code}")
    print(f"Response body: {response.text}")

def main():
    try:
        # Create test user and get their UID
        uid = create_test_user()
        
        # Get ID token
        id_token = get_id_token()
        print(f"\nGot ID token: {id_token[:20]}...")
        
        # Add a small delay to ensure token is ready
        time.sleep(1)
        
        # Test all endpoints
        test_endpoints(id_token)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 