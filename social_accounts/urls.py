from django.urls import path
from .views import YoutubeAuthConnectView, FacebookAuthConnectView

urlpatterns = [
    path('google/connect/', YoutubeAuthConnectView.as_view(), name='google-auth-connect'),
    path('facebook/connect/', FacebookAuthConnectView.as_view(), name='facebook-auth-connect'),
]
