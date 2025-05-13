from rest_framework import serializers

from social_accounts.models import SocialAccount


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = [
            "user",
            "account_type",
            "expires_at",
            "token_type",
        ]
        # make all fields read only
        read_only_fields = [
            "user",
            "account_type",
            "expires_at",
            "token_type",
        ]

class GoogleAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    redirect_uri = serializers.URLField(required=True)
    brand = serializers.PrimaryKeyRelatedField(
        queryset=SocialAccount.objects.all(),
    )

class FacebookAuthCodeSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    brand = serializers.PrimaryKeyRelatedField(
        queryset=SocialAccount.objects.all(),
    )
