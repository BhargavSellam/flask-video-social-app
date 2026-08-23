import os
import uuid
from pathlib import Path
from flask import current_app, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"mp4", "webm", "mov", "m4v"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_video(file):
    if not file or not file.filename:
        raise ValueError("No video file selected.")

    if not allowed_file(file.filename):
        raise ValueError("Unsupported video type. Use MP4, WEBM, MOV or M4V.")

    safe_name = secure_filename(file.filename)
    ext = Path(safe_name).suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"

    if current_app.config.get("USE_AZURE_STORAGE"):
        return _save_azure(file, filename)

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    destination = upload_folder / filename
    file.save(destination)

    return url_for("static", filename=f"uploads/{filename}"), "local"

def _save_azure(file, filename):
    connection_string = current_app.config.get("AZURE_STORAGE_CONNECTION_STRING")
    container_name = current_app.config.get("AZURE_STORAGE_CONTAINER", "videos")

    if not connection_string:
        raise ValueError("Azure storage is enabled but no connection string is configured.")

    from azure.storage.blob import BlobServiceClient, ContentSettings

    service = BlobServiceClient.from_connection_string(connection_string)
    container = service.get_container_client(container_name)

    try:
        container.create_container()
    except Exception:
        pass

    blob = container.get_blob_client(filename)
    content_type = file.mimetype or "video/mp4"

    blob.upload_blob(
        file.stream,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )

    return blob.url, "azure"
