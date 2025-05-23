import google_auth_oauthlib
from google.oauth2 import id_token
import requests
from django.conf import settings


class GoogleAuthHelper:
    """
    A helper class to encapsulate Google OAuth 2.0 authentication logic.
    Handles exchanging the authorization code for tokens and verifying the ID token.
    """
    def __init__(self, redirect_uri):
        self.client_id =  settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = redirect_uri
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ]

    def verify_and_get_user_info(self, auth_code):
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": self.redirect_uri,
            }
        }

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )

        flow.fetch_token(code=auth_code)

        id_info = flow.id_token

        id_info = id_token.verify_oauth2_token(
            id_info, requests.Request(), self.client_id
        )

        # Extract user information from the verified ID token
        email = id_info.get('email')
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        google_id = id_info.get('sub') # 'sub' is the unique Google user ID

        if not email:
            raise ValueError("Email not found in ID token")

        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }
