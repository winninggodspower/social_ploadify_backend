import requests
from django.conf import settings

from social_accounts.services import SocialAccountService


class FacebookService(SocialAccountService):
    CLIENT_ID = settings.FACEBOOK_CLIENT_ID
    CLIENT_SECRET = settings.FACEBOOK_CLIENT_SECRET

    @classmethod
    def refresh_access_token(self, refresh_token):
        return None, None, None

    @classmethod
    def exchange_short_lived_token(cls, short_lived_token):
        # First verify permissions with short-lived token
        is_valid, missing_permissions = cls.verify_granted_scope(short_lived_token)

        if not is_valid:
            raise ValueError(
                f"Missing required Facebook permissions: {', '.join(missing_permissions)}"
            )

        # If permissions are valid, proceed with token exchange
        response = requests.get(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": cls.CLIENT_ID,
                "client_secret": cls.CLIENT_SECRET,
                "fb_exchange_token": short_lived_token,
            },
        )
        data = response.json()
        print(data)

        if "access_token" not in data:
            raise ValueError(data.get("error", {}).get("message", "Unknown error"))

        return data["access_token"], int(data["expires_in"])

    @classmethod
    def verify_granted_scope(cls, access_token):
        """
        Verify the permissions granted to the access token
        Returns tuple of (is_valid, missing_scopes)
        """
        required_permissions = {
            "public_profile",
            "publish_video",
        }

        response = requests.get(
            "https://graph.facebook.com/v18.0/me/permissions",
            params={"access_token": access_token},
        )
        data = response.json()

        if "data" not in data:
            raise ValueError(
                data.get("error", {}).get("message", "Failed to verify permissions")
            )

        # Get granted permissions that are status: 'granted'
        granted_permissions = {
            perm["permission"] for perm in data["data"] if perm["status"] == "granted"
        }

        # Find missing permissions
        missing_permissions = required_permissions - granted_permissions

        return (not bool(missing_permissions), missing_permissions)

    @classmethod
    def get_facebook_pages(cls, access_token):
        # returns list of users pages
        pass

    @classmethod
    def initialize_livestream(cls, access_token, title, description, status="LIVE_NOW"):
        """
        Initialize a Facebook livestream
        Returns: Dictionary containing stream details and credentials
        """
        try:
            response = requests.post(
                "https://graph.facebook.com/v18.0/me/live_videos",
                params={
                    "access_token": access_token,
                    "status": status,
                    "title": title,
                    "description": description,
                },
            )
            data = response.json()

            if "id" not in data:
                raise ValueError(
                    data.get("error", {}).get("message", "Failed to create livestream")
                )

            return {
                "video_id": data.get("id"),
                "title": title,
                "description": description,
                "stream_url": data.get("stream_url"),  # RTMP URL
                "secure_stream_url": data.get("secure_stream_url"),  # RTMPS URL
                "status": status,
            }

        except requests.RequestException as e:
            raise ValueError(f"Failed to initialize Facebook livestream: {str(e)}")
