
import os
import base64

from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

load_dotenv()

key_hex = os.getenv("ENCRYPTION_KEY")

if not key_hex:
    raise RuntimeError("ENCRYPTION_KEY belum diatur di .env")

KEY = bytes.fromhex(key_hex)

if len(KEY) != 32:
    raise ValueError("Kunci AES harus berukuran 32 byte")


def encrypt_data(plaintext: str) -> tuple[str, str]:
    aes = AESGCM(KEY)
    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode("utf-8"),
        None
    )

    return (
        base64.b64encode(nonce).decode("utf-8"),
        base64.b64encode(ciphertext).decode("utf-8")
    )


def decrypt_data(nonce_b64: str, ciphertext_b64: str) -> str:
    aes = AESGCM(KEY)

    nonce = base64.b64decode(nonce_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    plaintext = aes.decrypt(nonce, ciphertext, None)

    return plaintext.decode("utf-8")
