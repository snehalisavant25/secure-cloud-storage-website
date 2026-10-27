import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_FILE = "secret.key"

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()

    key = AESGCM.generate_key(bit_length=256)
    with open(KEY_FILE, "wb") as f:
        f.write(key)

    return key

def encrypt_file(input_path, output_path):
    key = load_key()
    nonce = os.urandom(12)

    with open(input_path, "rb") as f:
        data = f.read()

    encrypted = AESGCM(key).encrypt(nonce, data, None)

    with open(output_path, "wb") as f:
        f.write(nonce + encrypted)

def decrypt_file(input_path, output_path):
    key = load_key()

    with open(input_path, "rb") as f:
        data = f.read()

    nonce = data[:12]
    encrypted = data[12:]
    decrypted = AESGCM(key).decrypt(nonce, encrypted, None)

    with open(output_path, "wb") as f:
        f.write(decrypted)