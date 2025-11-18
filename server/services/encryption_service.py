import os
import base64
import logging
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import Config


class EncryptionService:
    """Handles all encryption/decryption operations"""
    
    def __init__(self):
        self._private_key = None
        self._load_or_generate_keys()
    
    def _load_or_generate_keys(self):
        """Load existing RSA key or generate new one."""
        if os.path.exists(Config.PRIVATE_KEY_PATH):
            with open(Config.PRIVATE_KEY_PATH, "rb") as f:
                self._private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend()
                )
            logging.info("Loaded existing RSA private key")
        else:
            self._generate_new_keys()
    
    def _generate_new_keys(self):
        """Generate new RSA key pair."""
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Save private key
        private_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        try:
            with open(Config.PRIVATE_KEY_PATH, "wb") as f:
                f.write(private_pem)
        except OSError as e:
            logging.error(f"Failed to save private key: {e}")
        
        # Save public key
        public_pem = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        try:
            with open(Config.PUBLIC_KEY_PATH, "wb") as f:
                f.write(public_pem)
            logging.info("Generated new RSA key pair")
            logging.warning(
                "Distribute this public key to clients:\n%s",
                public_pem.decode("utf-8")
            )
        except OSError as e:
            logging.error(f"Failed to save public key: {e}")
    
    def get_public_key_pem(self):
        """Get public key in PEM format."""
        return self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    
    def decrypt_session_key(self, encrypted_key_b64):
        """Decrypt AES session key using RSA private key."""
        try:
            enc_bytes = base64.b64decode(encrypted_key_b64.encode("utf-8"))
            aes_key = self._private_key.decrypt(
                enc_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return aes_key
        except Exception as e:
            logging.error(f"Failed to decrypt session key: {e}")
            raise
    
    @staticmethod
    def pkcs7_unpad(padded: bytes) -> bytes:
        """Remove PKCS7 padding."""
        pad_len = padded[-1]
        return padded[:-pad_len]
    
    @staticmethod
    def aes_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-CBC."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        return EncryptionService.pkcs7_unpad(padded)