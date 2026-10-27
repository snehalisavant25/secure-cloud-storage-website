import os
import hashlib
from file_utils import split_file, reconstruct_file

os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

with open("uploads/sample.txt", "w") as f:
    f.write("Secure Cloud Storage Project " * 100000)

blocks = split_file("uploads/sample.txt", "uploads/blocks")
reconstruct_file(blocks, "downloads/recovered.txt")

def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

print("Blocks created:", len(blocks))
print("Files match:", sha256("uploads/sample.txt") == sha256("downloads/recovered.txt"))