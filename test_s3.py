from s3_utils import upload_file, download_file

upload_file("uploads/sample.enc", "test/sample.enc")

download_file("test/sample.enc", "downloads/cloud_sample.enc")

with open("uploads/sample.enc", "rb") as f:
    original = f.read()

with open("downloads/cloud_sample.enc", "rb") as f:
    downloaded = f.read()

print("Files match:", original == downloaded)