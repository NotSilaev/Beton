import hashlib
import secrets
import base64


def hashAuthToken(token: str, salt: bytes = None) -> tuple[str, str]:
    """
    Hash a token using SHA-256 with salt.

    :param token: The plain text token to hash
    :param salt: Optional salt bytes (if None, generates new salt)
    """

    if salt is None:
        salt = secrets.token_bytes(16)
    
    # Combine salt and token, then hash
    token_bytes = token.encode('utf-8')
    hasher = hashlib.sha256()
    hasher.update(salt + token_bytes)
    hashed = hasher.digest()
    
    # Return base64 encoded hash and hex encoded salt
    return base64.b64encode(hashed).decode('utf-8'), salt.hex()
