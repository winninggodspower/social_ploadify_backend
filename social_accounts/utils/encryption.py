from cryptography.fernet import Fernet
from django.conf import settings

FERNET_KEY = settings.FERNET_SECRET_KEY  # Must be 32 url-safe base64-encoded bytes
fernet = Fernet(FERNET_KEY)


def encrypt_text(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()


def decrypt_text(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
