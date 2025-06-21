from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import boto3
import io

# Create the FastAPI app
app = FastAPI()

# Serve static files (CSS) from the 'static' folder
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up templates (HTML files) from the 'templates' folder
templates = Jinja2Templates(directory='templates')

# Simple in-memory storage for users (in real apps, you'd use a database)
users = {}

# S3 bucket name
S3_BUCKET = 'my-s3-real-bucket'

# S3 client
s3_client = boto3.client('s3')

@app.get('/')
def home(request: Request):
    """Show the home page with login/register options"""
    return templates.TemplateResponse('home.html', {'request': request})

@app.get('/register')
def register_page(request: Request):
    """Show the registration page"""
    return templates.TemplateResponse('register.html', {'request': request})

@app.post('/register')
def register_user(request: Request, username: str = Form(), email: str = Form(), password: str = Form()):
    """Handle user registration"""
    if username in users:
        return templates.TemplateResponse('register.html', {
            'request': request, 
            'error': 'Username already exists!'
        })
    users[username] = {
        'username': username,
        'email': email,
        'password': password
    }
    return RedirectResponse('/login', status_code=302)

@app.get('/login')
def login_page(request: Request):
    """Show the login page"""
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/login')
def login_user(request: Request, username: str = Form(), password: str = Form()):
    """Handle user login"""
    if username in users and users[username]['password'] == password:
        # In real apps, you'd set a proper session cookie
        response = RedirectResponse('/profile?user=' + username, status_code=302)
        return response
    else:
        return templates.TemplateResponse('login.html', {
            'request': request, 
            'error': 'Wrong username or password!'
        })

@app.get('/profile')
def profile_page(request: Request, user: str = None):
    """Show the user profile page"""
    # Get user from query param (for demo)
    if not user or user not in users:
        return RedirectResponse('/login')
    user_data = users[user]
    # List files in S3 for this user
    files = []
    prefix = f"{user}/"
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        for obj in response.get('Contents', []):
            files.append(obj['Key'].split('/', 1)[-1])
    except Exception:
        pass
    return templates.TemplateResponse('profile.html', {
        'request': request,
        'user': user_data,
        'files': files,
        'username': user
    })

@app.post('/upload')
def upload_file(request: Request, user: str = Form(), file: UploadFile = File(...)):
    """Handle file upload and upload to S3"""
    if not user or user not in users:
        return RedirectResponse('/login')
    # Upload file to S3 under user's folder
    s3_key = f"{user}/{file.filename}"
    s3_client.upload_fileobj(file.file, S3_BUCKET, s3_key)
    return RedirectResponse(f'/profile?user={user}', status_code=302)

@app.post('/send_message')
def send_message(request: Request):
    """Handle sending a message (simplified)"""
    print("Message sent! (This is just a demo)")
    return RedirectResponse('/profile', status_code=302)

@app.get('/download/{filename}')
def download_file(filename: str, user: str = None):
    """Download a file from S3 for the user"""
    if not user or user not in users:
        return RedirectResponse('/login')
    s3_key = f"{user}/{filename}"
    fileobj = io.BytesIO()
    try:
        s3_client.download_fileobj(S3_BUCKET, s3_key, fileobj)
        fileobj.seek(0)
        return StreamingResponse(fileobj, media_type='application/octet-stream', headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        })
    except Exception as e:
        return HTMLResponse(f"<h2>File not found or error: {e}</h2>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 