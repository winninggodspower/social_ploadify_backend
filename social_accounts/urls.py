from django.urls import path
from .views import (
    YoutubeAuthConnectView,
    FacebookAuthConnectView,
    InstagramAuthConnectView,
    TiktokAuthConnectView,
    LinkedinAuthConnectView,
)

urlpatterns = [
    path('google/connect/', YoutubeAuthConnectView.as_view(), name='google-auth-connect'),
    path('facebook/connect/', FacebookAuthConnectView.as_view(), name='facebook-auth-connect'),
    path('instagram/connect/', InstagramAuthConnectView.as_view(), name='instagram-auth-connect'),
    path('tiktok/connect/', TiktokAuthConnectView.as_view(), name='tiktok-auth-connect'),
    path('linkedin/connect/', LinkedinAuthConnectView.as_view(), name='linkedin-auth-connect'),
]
