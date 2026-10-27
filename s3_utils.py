import os
import boto3

BUCKET_NAME = "secure-storage-snehali-2725-665808487911-ap-south-1-an"

s3 = boto3.client("s3")

def upload_file(file_path, object_name):
    s3.upload_file(file_path, BUCKET_NAME, object_name)
    print("Uploaded:", object_name)

def download_file(object_name, output_path):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    s3.download_file(BUCKET_NAME, object_name, output_path)
    print("Downloaded:", object_name)