import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    logger.info("Firebase Admin SDK initialized successfully")
except ValueError as e:
    logger.warning(f"Firebase Admin SDK already initialized: {str(e)}")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
    raise

# Security scheme for FastAPI
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        logger.debug(f"Received token: {token[:20]}...")
        
        # Verify the ID token
        try:
            logger.debug("Attempting to verify ID token...")
            decoded_token = auth.verify_id_token(token)
            logger.debug(f"Successfully decoded token: {json.dumps(decoded_token, indent=2)}")
            
            # Extract user information
            user_info = {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email", ""),
                "email_verified": decoded_token.get("email_verified", False)
            }
            logger.debug(f"Extracted user info: {json.dumps(user_info, indent=2)}")
            return user_info
            
        except auth.InvalidIdTokenError as e:
            logger.error(f"Invalid ID token error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid ID token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except auth.ExpiredIdTokenError as e:
            logger.error(f"Expired ID token error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Expired ID token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except Exception as e:
        logger.error(f"General error in verify_token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) 