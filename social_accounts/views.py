from datetime import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from social_accounts.models import SocialAccount
from social_accounts.serializers import FacebookAuthCodeSerializer, GoogleAuthCodeSerializer
from social_accounts.services.facebook_service import FacebookService
from social_accounts.services.youtube_service import YoutubeService
from social_ploadify_backend.responses import CustomErrorResponse, CustomSuccessResponse

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


# --- Facebook Auth and Stream Endpoints ---
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
                serializer.validated_data["access_token"]
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
