from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse, StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import io
from app.dependencies import require_cognito_token
from app.services.dynamodb import get_user_profile
from app.services.s3 import upload_fileobj, list_user_files, download_fileobj
from app.config import S3_BUCKET
from urllib.parse import quote

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get('/profile')
def profile_page(request: Request, user: Optional[str] = None, token_data: dict = Depends(require_cognito_token)):
    if not user:
        return RedirectResponse('/login')
    user_data = get_user_profile(user)
    if not user_data:
        return RedirectResponse('/login')
    files = []
    prefix = f"{user}/"
    try:
        files = list_user_files(prefix)
    except Exception:
        pass
    return templates.TemplateResponse('profile.html', {
        'request': request,
        'user': user_data,
        'files': files,
        'username': user
    })

@router.post('/upload')
def upload_file(request: Request, user: str = Form(), file: UploadFile = File(...), token_data: dict = Depends(require_cognito_token)):
    if not user:
        return RedirectResponse('/login')
    s3_key = f"{user}/{file.filename}"
    upload_fileobj(file.file, s3_key)
    return RedirectResponse(f'/profile?user={user}', status_code=302)

@router.get('/download/{filename}')
def download_file(filename: str, user: Optional[str] = None):
    if not user:
        return RedirectResponse('/login')
    s3_key = f"{user}/{filename}"
    fileobj = io.BytesIO()
    try:
        download_fileobj(s3_key, fileobj)
        fileobj.seek(0)
        encoded_filename = quote(filename)
        ascii_filename = filename.encode('ascii', 'ignore').decode('ascii') or 'downloaded_file'
        headers = {
            'Content-Disposition': f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        }
        return StreamingResponse(fileobj, media_type='application/octet-stream', headers=headers)
    except Exception as e:
        return HTMLResponse(f"<h2>File not found or error: {e}</h2>", status_code=404)
