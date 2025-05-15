from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from social_accounts.models import SocialAccount
from social_accounts.serializers import FacebookAuthCodeSerializer, GoogleAuthCodeSerializer, InstagramAuthCodeSerializer
from social_accounts.services.facebook_service import FacebookService
from social_accounts.services.instagram_service import InstagramService
from social_accounts.services.tiktok_service import TiktokService
from social_accounts.services.youtube_service import YoutubeService
from social_ploadify_backend.responses import CustomErrorResponse, CustomSuccessResponse
from social_accounts.services.linkedin_service import LinkedinService
from social_accounts.serializers import LinkedinAuthCodeSerializer

# Create your views here.

# --- Youtube Auth View ---
class YoutubeAuthConnectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GoogleAuthCodeSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, *args, **kwargs):
        # vaidate data
        serializer = GoogleAuthCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # --- Brand ownership verification ---
        brand = serializer.validated_data["brand"]
        if brand.user != request.user:
            return CustomErrorResponse(
                {
                    "message": "You do not have permission to access this brand.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            credentials, missing_scopes = YoutubeService.exchange_code_for_token(
                auth_code=serializer.validated_data["code"],
                google_auth_redirect_uri=serializer.validated_data["redirect_uri"],
            )
        except ValueError as e:
            return CustomErrorResponse(
                {
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if missing_scopes:
            raise CustomErrorResponse(
                {
                    "message": "Missing required permissions.",
                    "missing_scopes": list(missing_scopes),
                }
            )

        # Save the credentials to the database
        social_account = SocialAccount.objects.update_or_create(
            user=request.user,
            account_type="youtube",
            brand=brand,
            defaults={
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_at": credentials.expiry,
                "scope": " ".join(credentials.scopes),
            },
        )

        return CustomSuccessResponse(
            {
                "message": "YouTube account successfully connected",
                "account_type": "youtube",
                "is_connected": True,
            },
            status=status.HTTP_200_OK,
        )


# --- Facebook Auth View ---
class FacebookAuthConnectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FacebookAuthCodeSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # --- Brand ownership verification ---
        brand = serializer.validated_data["brand"]
        if brand.user != request.user:
            return CustomErrorResponse(
                {
                    "message": "You do not have permission to access this brand.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            long_lived_token, expires_in = FacebookService.exchange_short_lived_token(
                serializer.validated_data["short_lived_access_token"]
            )
        except ValueError as e:
            return CustomErrorResponse(
                {
                    "message": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # save token to db
        social_account = SocialAccount.objects.get_or_create(
            user=request.user,
            account_type="facebook",
            brand=brand,
            defaults={
                "access_token": long_lived_token,
                "expires_at": datetime.datetime.today()
                + datetime.timedelta(seconds=expires_in),
            },
        )

        return CustomSuccessResponse(
            {
                "message": "Facebook account successfully connected",
                "account_type": "facebook",
                "is_connected": True,
            }
        )

class InstagramAuthConnectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InstagramAuthCodeSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # --- Brand ownership verification ---
        brand = serializer.validated_data["brand"]
        if brand.user != request.user:
            return CustomErrorResponse(
                {
                    "message": "You do not have permission to access this brand.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            credentials, missing_scopes = InstagramService.exchange_code_for_token(
                auth_code=serializer.validated_data["code"],
                google_auth_redirect_uri=serializer.validated_data["redirect_uri"],
            )
        except ValueError as e:
            return CustomErrorResponse(
                {
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if missing_scopes:
            raise CustomErrorResponse(
                {
                    "message": "Missing required permissions.",
                    "missing_scopes": list(missing_scopes),
                }
            )

        # Save the credentials to the database
        social_account = SocialAccount.objects.update_or_create(
            user=request.user,
            account_type="instagram",
            brand=brand,
            defaults={
                "access_token": credentials["access_token"],
                "expires_at": datetime.datetime.today()
                + datetime.timedelta(seconds=credentials["expires_in"]),
            },
        )

        return CustomSuccessResponse(
            {
                "message": "Instagram account successfully connected",
                "account_type": "instagram",
                "is_connected": True,
            }
        )

class TiktokAuthConnectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InstagramAuthCodeSerializer

    def post(self, request):
        # Deserialize the incoming data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract the authorization code
        code = serializer.validated_data["code"]
        try:
            # Exchange the authorization code for an access token
            token_data = TiktokService.exchange_code_for_token(code)
        except ValueError as e:
            return CustomSuccessResponse({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Extract token details
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data["expires_in"]
        open_id = token_data["open_id"]
        scope = token_data["scope"]

        # Calculate the expiration date
        expires_at = timezone.now() + timedelta(seconds=expires_in)

        # Save the credentials to the database (SocialAccount model)
        social_account, created = SocialAccount.objects.update_or_create(
            user=request.user,
            account_type="tiktok",
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "open_id": open_id,
                "scope": scope,
            },
        )

        return CustomSuccessResponse({
            "message": "TikTok account successfully connected",
            "account_type": "tiktok",
            "is_connected": True,
        }, status=status.HTTP_200_OK)

class LinkedinAuthConnectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LinkedinAuthCodeSerializer

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # --- Brand ownership verification ---
        brand = serializer.validated_data["brand"]
        if brand.user != request.user:
            return CustomErrorResponse(
                {"message": "You do not have permission to access this brand."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            token_data = LinkedinService.exchange_code_for_token(
                serializer.validated_data["code"],
                serializer.validated_data["redirect_uri"],
            )
        except ValueError as e:
            return CustomErrorResponse(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save the credentials to the database
        expires_at = timezone.now() + timedelta(seconds=token_data["expires_in"])
        social_account, created = SocialAccount.objects.update_or_create(
            user=request.user,
            account_type="linkedin",
            brand=brand,
            defaults={
                "access_token": token_data["access_token"],
                "expires_at": expires_at,
                "scope": token_data.get("scope", ""),
            },
        )

        return CustomSuccessResponse(
            {
                "message": "LinkedIn account successfully connected",
                "account_type": "linkedin",
                "is_connected": True,
            },
            status=status.HTTP_200_OK,
        )
