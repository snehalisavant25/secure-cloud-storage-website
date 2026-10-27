from crypto_utils import encrypt_file, decrypt_file

encrypt_file("uploads/sample.txt", "uploads/sample.enc")
decrypt_file("uploads/sample.enc", "downloads/decrypted.txt")

with open("uploads/sample.txt", "rb") as f:
    original = f.read()

with open("downloads/decrypted.txt", "rb") as f:
    recovered = f.read()

print("Encryption completed")
print("Decryption completed")
print("Files match:", original == recovered)