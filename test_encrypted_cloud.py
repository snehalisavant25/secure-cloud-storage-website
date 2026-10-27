import os
import json
import uuid
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from s3_utils import upload_file, download_file

BLOCK_SIZE = 1024 * 1024
KEY_FILE = "secret.key"

os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(AESGCM.generate_key(bit_length=256))

with open(KEY_FILE, "rb") as f:
    key = f.read()

aes = AESGCM(key)

source = "uploads/cloud_test_sample.txt"
recovered = "downloads/recovered_sample.txt"

if not os.path.exists(source):
    with open(source, "wb") as f:
        f.write(b"Secure cloud storage test data.\n" * 100000)

file_id = uuid.uuid4().hex
prefix = f"encrypted-tests/{file_id}"
manifest = {"blocks": []}

os.makedirs("uploads/encrypted_blocks", exist_ok=True)
os.makedirs("downloads/encrypted_blocks", exist_ok=True)

with open(source, "rb") as f:
    index = 0
    while True:
        data = f.read(BLOCK_SIZE)
        if not data:
            break

        nonce = os.urandom(12)
        encrypted = nonce + aes.encrypt(nonce, data, None)

        local_block = f"uploads/encrypted_blocks/block_{index:04d}.enc"
        object_key = f"{prefix}/block_{index:04d}.enc"

        with open(local_block, "wb") as block:
            block.write(encrypted)

        upload_file(local_block, object_key)
        manifest["blocks"].append(object_key)
        index += 1

manifest_path = "uploads/manifest.json"

with open(manifest_path, "w") as f:
    json.dump(manifest, f)

manifest_key = f"{prefix}/manifest.json"
upload_file(manifest_path, manifest_key)

download_file(manifest_key, "downloads/manifest.json")

with open("downloads/manifest.json", "r") as f:
    downloaded_manifest = json.load(f)

with open(recovered, "wb") as output:
    for index, object_key in enumerate(downloaded_manifest["blocks"]):
        encrypted_path = f"downloads/encrypted_blocks/block_{index:04d}.enc"
        download_file(object_key, encrypted_path)

        with open(encrypted_path, "rb") as block:
            encrypted = block.read()

        nonce = encrypted[:12]
        ciphertext = encrypted[12:]
        decrypted = aes.decrypt(nonce, ciphertext, None)
        output.write(decrypted)

with open(source, "rb") as f:
    original = f.read()

with open(recovered, "rb") as f:
    result = f.read()

print("\nTotal blocks:", len(manifest["blocks"]))
print("Encryption: AES-GCM")
print("Cloud upload and download: Successful")
print("Files match:", original == result)