from fastapi import FastAPI, Request, Form, Depends, status, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import authenticate_user, register_user, get_current_user, verify_2fa
from models import User, UserCreate, UserLogin
from storage import save_file
from sns import send_sns_message
import os

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

@app.get('/')
def root():
    return RedirectResponse('/login')

@app.get('/login')
def login_get(request: Request):
    return templates.TemplateResponse('login.html', {'request': request, 'error': None})

@app.post('/login')
def login_post(request: Request, username: str = Form(...), password: str = Form(...), totp: str = Form(None)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid username or password'})
    if user['2fa_enabled']:
        if not totp or not verify_2fa(user, totp):
            return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid 2FA code'})
    response = RedirectResponse('/profile', status_code=status.HTTP_302_FOUND)
    response.set_cookie('user', user['username'])
    return response

@app.get('/register')
def register_get(request: Request):
    return templates.TemplateResponse('register.html', {'request': request, 'error': None})

@app.post('/register')
def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    result, error = register_user(username, email, password)
    if not result:
        return templates.TemplateResponse('register.html', {'request': request, 'error': error})
    return RedirectResponse('/login', status_code=status.HTTP_302_FOUND)

@app.get('/profile')
def profile(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    # List uploaded files
    user_dir = os.path.join('uploads', user['username'])
    files = []
    if os.path.exists(user_dir):
        files = os.listdir(user_dir)
    return templates.TemplateResponse('profile.html', {
        'request': request,
        'user': user,
        'files': files,
        'error': None,
        'success': None
    })

@app.post('/upload')
def upload_file(request: Request, file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    save_file(user['username'], file)
    return RedirectResponse('/profile', status_code=status.HTTP_302_FOUND)

@app.get('/download/{filename}')
def download_file(filename: str, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    file_path = os.path.join('uploads', user['username'], filename)
    if not os.path.exists(file_path):
        return RedirectResponse('/profile')
    return FileResponse(file_path, filename=filename)

@app.get('/preview/{filename}')
def preview_file(filename: str, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    file_path = os.path.join('uploads', user['username'], filename)
    if not os.path.exists(file_path):
        return RedirectResponse('/profile')
    # Only allow preview for images and text
    ext = filename.split('.')[-1].lower()
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
        return templates.TemplateResponse('preview_image.html', {'request': request, 'filename': filename, 'user': user})
    elif ext in ['txt', 'md', 'log', 'py', 'json', 'csv']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return templates.TemplateResponse('preview_text.html', {'request': request, 'filename': filename, 'content': content, 'user': user})
    else:
        return RedirectResponse(f'/download/{filename}')

@app.post('/send_message')
def send_message(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    send_sns_message(user['email'], f"Hello {user['username']}! This is your message.")
    return RedirectResponse('/profile', status_code=status.HTTP_302_FOUND)

@app.get('/edit_profile')
def edit_profile_get(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    return templates.TemplateResponse('edit_profile.html', {'request': request, 'user': user, 'error': None, 'success': None})

@app.post('/edit_profile')
def edit_profile_post(request: Request, email: str = Form(...), phone: str = Form(...), address: str = Form(...), user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse('/login')
    user['email'] = email
    user['phone'] = phone
    user['address'] = address
    return templates.TemplateResponse('edit_profile.html', {'request': request, 'user': user, 'error': None, 'success': 'Profile updated successfully.'}) 