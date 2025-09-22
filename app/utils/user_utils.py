from fastapi import UploadFile, File
import os
import uuid

UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_avatar(file: UploadFile) -> str:
    # 获取扩展名
    ext = os.path.splitext(file.filename)[1]

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    return f"/{UPLOAD_DIR}{filename}"
