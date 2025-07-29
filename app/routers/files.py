# routers/files.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.file import File as FileModel
from ..services.ftp_client import FTPClient
from ..schemas.file import FileRead
from ..security import verify_token
import aiofiles
import tempfile
import os
import shutil

router = APIRouter(tags=["files"])
security = HTTPBearer()

FTP_CONFIG = dict(host="3117204815.cloudydl.com", port=21,
                  user="pz21770", password="IxiIvlLS")


@router.post("/upload", response_model=FileRead)
async def upload_file(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # بررسی اعتبار توکن
    payload = verify_token(credentials.credentials)
    user_id = int(payload.sub)

    # ساخت مسیر موقت سازگار با همه سیستم‌عامل‌ها
    try:
        suffix = os.path.splitext(file.filename)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name

        # ذخیره فایل روی دیسک موقت
        async with aiofiles.open(temp_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        # آپلود به FTP
        ftp = FTPClient(**FTP_CONFIG)
        remote_path = f"public_html/uploads/{user_id}/{file.filename}"
        await ftp.upload(temp_path, remote_path)

        # پاک کردن فایل موقت
        os.remove(temp_path)
        remote_path = remote_path.split("/")
        print(remote_path)
        remote_path.pop(0)
        print(remote_path)
        remote_path = "/".join(remote_path)
        print(remote_path)
        # گرفتن URL عمومی (در صورت نیاز)
        url = await ftp.get_public_url(remote_path)

        # ذخیره رکورد در دیتابیس
        db_file = FileModel(
            user_id=user_id,
            filename=file.filename,
            remote_path=remote_path,
        )
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)

        return db_file

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=list[FileRead])
async def list_files(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    user_id = int(payload.sub)
    result = await db.execute(select(FileModel).where(FileModel.user_id == user_id))
    return result.scalars().all()


@router.get("/{file_id}", response_model=FileRead)
async def get_file(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    user_id = int(payload.sub)
    result = await db.execute(select(FileModel).where(FileModel.id == file_id, FileModel.user_id == user_id))
    db_file = result.scalar_one_or_none()
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return db_file


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    user_id = int(payload.sub)
    result = await db.execute(select(FileModel).where(FileModel.id == file_id, FileModel.user_id == user_id))
    db_file = result.scalar_one_or_none()
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    ftp = FTPClient(**FTP_CONFIG)
    await ftp.upload(None, None)  # implement delete logic if supported
    await db.delete(db_file)
    await db.commit()
    return {"msg": "Deleted"}
