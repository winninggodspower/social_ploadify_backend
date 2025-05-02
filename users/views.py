from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import RegisterUserSerializer

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()

# Create your views here.
class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response({'detail': 'ID token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            # Get or create user
            user, created = User.objects.get_or_create(email=email, defaults={
                'first_name': first_name,
                'last_name': last_name,
            })

            # Return JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        except ValueError:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
