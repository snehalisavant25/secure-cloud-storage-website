import os
import uuid
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from s3_utils import upload_file, download_file

app = Flask(__name__)
app.secret_key = os.urandom(32)

BLOCK_SIZE = 1024 * 1024
KEY_FILE = "secret.key"
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(AESGCM.generate_key(bit_length=256))

with open(KEY_FILE, "rb") as f:
    key = f.read()

aes = AESGCM(key)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if not uploaded_file or not uploaded_file.filename:
            flash("Please select a file.")
            return redirect(url_for("index"))

        file_id = uuid.uuid4().hex
        original_name = os.path.basename(uploaded_file.filename)
        source_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{original_name}")
        uploaded_file.save(source_path)

        block_keys = []

        with open(source_path, "rb") as source:
            index = 0

            while True:
                data = source.read(BLOCK_SIZE)

                if not data:
                    break

                nonce = os.urandom(12)
                encrypted = nonce + aes.encrypt(nonce, data, None)

                block_path = os.path.join(
                    UPLOAD_FOLDER, f"{file_id}_block_{index:04d}.enc"
                )

                with open(block_path, "wb") as block:
                    block.write(encrypted)

                object_key = f"files/{file_id}/block_{index:04d}.enc"
                upload_file(block_path, object_key)
                block_keys.append(object_key)
                index += 1

        manifest_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_manifest.txt")

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(original_name + "\n")
            f.write(str(len(block_keys)) + "\n")
            f.write("\n".join(block_keys))

        manifest_key = f"files/{file_id}/manifest.txt"
        upload_file(manifest_path, manifest_key)

        flash(f"File uploaded and encrypted successfully. File ID: {file_id}")
        return redirect(url_for("index"))

    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    file_id = request.form.get("file_id", "").strip()

    if not file_id or any(c not in "0123456789abcdef" for c in file_id.lower()):
        flash("Enter a valid File ID.")
        return redirect(url_for("index"))

    manifest_key = f"files/{file_id}/manifest.txt"
    local_manifest = os.path.join(DOWNLOAD_FOLDER, f"{file_id}_manifest.txt")

    try:
        download_file(manifest_key, local_manifest)

        with open(local_manifest, "r", encoding="utf-8") as f:
            original_name = os.path.basename(f.readline().strip())
            block_count = int(f.readline().strip())
            block_keys = [f.readline().strip() for _ in range(block_count)]

        if block_count < 1 or len(block_keys) != block_count or any(not k for k in block_keys):
            raise ValueError("Invalid manifest.")

        output_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}_{original_name}")

        with open(output_path, "wb") as output:
            for index, object_key in enumerate(block_keys):
                encrypted_path = os.path.join(
                    DOWNLOAD_FOLDER, f"{file_id}_block_{index:04d}.enc"
                )

                download_file(object_key, encrypted_path)

                with open(encrypted_path, "rb") as block:
                    encrypted = block.read()

                nonce = encrypted[:12]
                ciphertext = encrypted[12:]
                output.write(aes.decrypt(nonce, ciphertext, None))

        return send_file(output_path, as_attachment=True, download_name=original_name)

    except Exception:
        flash("Download failed. Check the File ID, AWS access, and local encryption key.")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False)