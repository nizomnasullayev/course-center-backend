import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Dict
from app.config import settings
import os


class FirebaseAuth:
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            cls._initialized = True
        else:
            print("Warning: Firebase credentials not found. Google authentication will not work.")
    
    @classmethod
    def verify_id_token(cls, id_token: str) -> Optional[Dict]:
        """
        Verify Firebase ID token and return user info
        
        Returns:
            Dict with user info: {
                'uid': str,
                'email': str,
                'name': str,
                'phone_number': str (optional)
            }
        """
        if not cls._initialized:
            cls.initialize()
        
        if not cls._initialized:
            raise Exception("Firebase not initialized")
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            
            # Get user info from Firebase
            user = auth.get_user(decoded_token['uid'])
            
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name') or user.display_name,
                'phone_number': decoded_token.get('phone_number') or user.phone_number,
            }
        except Exception as e:
            print(f"Firebase token verification failed: {e}")
            return None


firebase_auth = FirebaseAuth()