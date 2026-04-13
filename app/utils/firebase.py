import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Dict
from app.config import settings
from fastapi import HTTPException, status
import os


class FirebaseAuth:
    _initialized = False
    
    def initialize(self):
        """Initialize Firebase Admin SDK"""
        if FirebaseAuth._initialized:
            return
        
        if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            FirebaseAuth._initialized = True
        else:
            print("Warning: Firebase credentials not found. Google authentication will not work.")
    
    def verify_id_token(self, id_token: str) -> Dict:
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
        if not FirebaseAuth._initialized:
            self.initialize()
        
        if not FirebaseAuth._initialized:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not properly initialized on the server."
            )
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            
            # Get user info from Firebase
            user = auth.get_user(decoded_token['uid'])
            
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email') or user.email,
                'name': decoded_token.get('name') or user.display_name,
                'phone_number': decoded_token.get('phone_number') or user.phone_number,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Firebase token verification failed: {str(e)}"
            )


firebase_auth = FirebaseAuth()