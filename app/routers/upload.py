import os
import uuid
from datetime import datetime
from typing import List

import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Form
from pathlib import Path
from fastapi.security import HTTPBearer

from app.deps import get_current_admin, get_current_registered_user
from app.models import ImageModel, User
from app.schemas import ImageResponse, ImageListResponse

router = APIRouter(prefix="/admin/api/upload", tags=["api_upload"])
security = HTTPBearer()

UPLOAD_DIR = Path("upload/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_FILES_PER_UPLOAD = 10


@router.post("/image", response_model=ImageResponse)
async def upload_image(
        file: UploadFile = File(...),
        current_user=Depends(get_current_registered_user)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型{file.content_type}，请上传图片文件。"
        )

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超出限制{MAX_FILE_SIZE}字节，请上传较小的图片。"
        )

    await file.seek(0)

    file_uuid = uuid.uuid4()
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_uuid}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)

    image_url = f"/upload/images/{unique_filename}"

    try:
        image_obj = ImageModel(
            uuid=file_uuid,
            original_name=file.filename,
            filename=unique_filename,
            file_path=str(file_path),
            file_size=len(file_content),
            content_type=file.content_type,
            url=image_url,
            uploaded_by=current_user,
            uploaded_at=datetime.now()
        )
        await image_obj.save()

        return {
            "success": True,
            "message": "图片上传成功",
            "url": image_url,
            "uuid": str(file_uuid),
            "id": image_obj.id
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片上传失败: {str(e)}"
        )


@router.delete("/image/{image_id}")
async def delete_iamge(
        url: str = Form(...),
        current_user=Depends(get_current_registered_user)
):
    filename = os.path.basename(url)
    file_path = UPLOAD_DIR / filename

    try:
        image_obj = await ImageModel.filter(url=url).first()
        if not image_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图片不存在"
            )

        if image_obj.uploaded_by != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除该图片"
            )

        await image_obj.delete()

        return {
            "success": True,
            "message": "图片删除成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片删除失败: {str(e)}"
        )


@router.get("/images", response_model=list[ImageListResponse])
async def get_images(
        page: int = 1,
        size: int = 10,
        current_user=Depends(get_current_registered_user)
):
    try:
        offset = (page - 1) * size
        images = await ImageModel.filter(uploaded_by=current_user).order_by("-uploaded_at").offset(offset).limit(size).all()

        total = await ImageModel.filter(uploaded_by=current_user).count()

        items = []

        for image in images:
            items.append({
                "id": image.id,
                "uuid": image.uuid,
                "original_name": image.original_name,
                "filename": image.filename,
                "url": image.url,
                "file_size": image.file_size,
                "content_type": image.content_type,
                "uploaded_at": image.uploaded_at.isoformat()
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图片列表失败: {str(e)}"
        )


@router.post("/images/batch", response_model=List[ImageResponse])
async def upload_multiple_images(
        files: List[UploadFile] = File(...),
        current_user: User = Depends(get_current_registered_user)
):
    """批量上传图片"""
    # 检查文件数量限制
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"每次最多只能上传{MAX_FILES_PER_UPLOAD}张图片"
        )

    results = []

    for file in files:
        try:
            # 验证文件类型
            if file.content_type not in ALLOWED_TYPES:
                results.append({
                    "success": False,
                    "message": f"不支持的文件类型: {file.filename}",
                    "filename": file.filename
                })
                continue

            # 验证文件大小
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                results.append({
                    "success": False,
                    "message": f"文件太大: {file.filename}",
                    "filename": file.filename
                })
                continue

            # 重置文件指针
            await file.seek(0)

            # 生成唯一文件名和UUID
            file_uuid = uuid.uuid4()
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{file_uuid}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename

            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)

            # 创建图片记录
            image_url = f"/upload/images/{unique_filename}"

            # 创建图片记录到数据库
            image_obj = ImageModel(
                uuid=file_uuid,
                original_name=file.filename,
                filename=unique_filename,
                file_path=str(file_path),
                file_size=len(file_content),
                content_type=file.content_type,
                url=image_url,
                uploaded_by=current_user,
                uploaded_at=datetime.now()
            )
            await image_obj.save()

            results.append({
                "success": True,
                "message": "图片上传成功",
                "url": image_url,
                "uuid": str(image_obj.uuid),
                "id": image_obj.id,
                "filename": file.filename
            })
        except Exception as e:
            results.append({
                "success": False,
                "message": f"上传失败: {str(e)}",
                "filename": file.filename
            })

    return results
