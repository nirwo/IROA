"""
Credential encryption utilities for IROA
Provides encryption/decryption for stored credentials
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key_from_password(password: str, salt: bytes = None) -> bytes:
    """Generate a key from a password using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def get_or_create_encryption_key() -> bytes:
    """Get or create encryption key for credential storage"""
    key_file = "config/encryption.key"
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    
    # Create new key
    key = Fernet.generate_key()
    
    # Ensure config directory exists
    os.makedirs("config", exist_ok=True)
    
    # Save key to file
    with open(key_file, 'wb') as f:
        f.write(key)
    
    return key


def encrypt_credential(credential: str) -> str:
    """Encrypt a credential string"""
    if not credential:
        return ""
    
    key = get_or_create_encryption_key()
    f = Fernet(key)
    encrypted_bytes = f.encrypt(credential.encode())
    return base64.urlsafe_b64encode(encrypted_bytes).decode()


def decrypt_credential(encrypted_credential: str) -> str:
    """Decrypt a credential string"""
    if not encrypted_credential:
        return ""
    
    try:
        key = get_or_create_encryption_key()
        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_credential.encode())
        decrypted_bytes = f.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    except Exception as e:
        print(f"Failed to decrypt credential: {e}")
        return ""


def encrypt_integration_passwords(config: dict) -> dict:
    """Encrypt passwords in integration configuration"""
    encrypted_config = config.copy()
    
    for integration_type, settings in encrypted_config.items():
        if isinstance(settings, dict) and 'password' in settings:
            if settings['password'] and not settings['password'].startswith('enc_'):
                # Only encrypt if not already encrypted
                encrypted_password = encrypt_credential(settings['password'])
                settings['password'] = f"enc_{encrypted_password}"
    
    return encrypted_config


def decrypt_integration_passwords(config: dict) -> dict:
    """Decrypt passwords in integration configuration"""
    decrypted_config = config.copy()
    
    for integration_type, settings in decrypted_config.items():
        if isinstance(settings, dict) and 'password' in settings:
            if settings['password'] and settings['password'].startswith('enc_'):
                # Remove 'enc_' prefix and decrypt
                encrypted_password = settings['password'][4:]  # Remove 'enc_' prefix
                decrypted_password = decrypt_credential(encrypted_password)
                settings['password'] = decrypted_password
    
    return decrypted_config