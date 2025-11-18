import os
import base64
import secrets
from typing import Tuple, Optional
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def fetch_server_public_key(server_url: str) -> Optional[bytes]:
    """Fetch server's public key from /public_key endpoint."""
    try:
        import urllib.request
        url = f"{server_url.rstrip('/')}/public_key"
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read()
    except Exception:
        return None


def load_server_public_key_pem(server_url: Optional[str] = None) -> bytes:
    """Load server public key."""
    if server_url:
        fetched = fetch_server_public_key(server_url)
        if fetched:
            return fetched
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    pub_path = os.path.join(base_dir, "public_key.pem")
    if os.path.exists(pub_path):
        with open(pub_path, "rb") as f:
            return f.read()
    
    raise FileNotFoundError("Server public key not found")


def rsa_encrypt_with_server_public_key(data: bytes, server_url: Optional[str] = None) -> str:
    """Encrypt data with server's public key."""
    pem = load_server_public_key_pem(server_url)
    public_key = serialization.load_pem_public_key(pem, backend=default_backend())
    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(encrypted).decode("utf-8")


def generate_aes_key() -> bytes:
    """Generate AES-256 key."""
    return secrets.token_bytes(32)


def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    """Apply PKCS7 padding."""
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def _pkcs7_unpad(padded: bytes) -> bytes:
    """Remove PKCS7 padding."""
    pad_len = padded[-1]
    return padded[:-pad_len]


def aes_encrypt(data: bytes, key: bytes) -> Tuple[bytes, bytes]:
    """Encrypt data with AES-256-CBC."""
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded = _pkcs7_pad(data, 16)
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return ciphertext, iv


def aes_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt data with AES-256-CBC."""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    return _pkcs7_unpad(padded)