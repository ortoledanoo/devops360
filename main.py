from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import boto3
import io
import uuid

# =====================
# AWS CONFIGURATION
# =====================
# Set your AWS region here (must match where your DynamoDB table and S3 bucket are)
AWS_REGION = 'us-east-1'  # <-- CHANGE THIS TO YOUR REGION IF NEEDED

# =====================
# FASTAPI APP SETUP
# =====================
app = FastAPI()

# Serve static files (CSS) from the 'static' folder
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up templates (HTML files) from the 'templates' folder
templates = Jinja2Templates(directory='templates')

# =====================
# AWS CLIENTS
# =====================
S3_BUCKET = 'my-s3-real-bucket'      # Your S3 bucket name
DDB_TABLE = 'my-app-db'              # Your DynamoDB table name

# Create AWS clients/resources with explicit region
s3_client = boto3.client('s3', region_name=AWS_REGION)
ddb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = ddb.Table(DDB_TABLE)

# =====================
# ROUTES
# =====================

@app.get('/')
def home(request: Request):
    """
    Home page with links to login/register.
    """
    return templates.TemplateResponse('home.html', {'request': request})

@app.get('/register')
def register_page(request: Request):
    """
    Show the registration form.
    """
    return templates.TemplateResponse('register.html', {'request': request})

@app.post('/register')
def register_user(
    request: Request,
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    address: str = Form(),
    zip_code: str = Form(),
    profile_photo: UploadFile = File(None)
):
    """
    Handle user registration:
    - Check if user exists in DynamoDB
    - Upload profile photo to S3 (if provided)
    - Save user data to DynamoDB (including S3 photo URL)
    """
    # Check if user already exists
    resp = table.get_item(Key={'user_id': username})
    if 'Item' in resp:
        return templates.TemplateResponse('register.html', {
            'request': request,
            'error': 'Username already exists!'
        })
    # Upload profile photo to S3 (optional)
    photo_url = ''
    if profile_photo:
        # Create a unique S3 key for the photo
        photo_key = f"profile_photos/{username}_{uuid.uuid4()}_{profile_photo.filename}"
        s3_client.upload_fileobj(profile_photo.file, S3_BUCKET, photo_key)
        # Public S3 URL (if bucket is public or has proper permissions)
        photo_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{photo_key}"
    # Save user data to DynamoDB
    table.put_item(Item={
        'user_id': username,
        'email': email,
        'password': password,  # WARNING: In real apps, hash passwords!
        'address': address,
        'zip_code': zip_code,
        'profile_photo': photo_url
    })
    return RedirectResponse('/login', status_code=302)

@app.get('/login')
def login_page(request: Request):
    """
    Show the login form.
    """
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/login')
def login_user(request: Request, username: str = Form(), password: str = Form()):
    """
    Handle user login:
    - Fetch user from DynamoDB
    - Check password
    - Redirect to profile if successful
    """
    resp = table.get_item(Key={'user_id': username})
    user = resp.get('Item')
    if user and user['password'] == password:
        # In a real app, use sessions/cookies for authentication
        response = RedirectResponse(f'/profile?user={username}', status_code=302)
        return response
    else:
        return templates.TemplateResponse('login.html', {
            'request': request,
            'error': 'Wrong username or password!'
        })

@app.get('/profile')
def profile_page(request: Request, user: str = None):
    """
    Show the user's profile page:
    - Fetch user data from DynamoDB
    - List user's uploaded files from S3
    """
    if not user:
        return RedirectResponse('/login')
    resp = table.get_item(Key={'user_id': user})
    user_data = resp.get('Item')
    if not user_data:
        return RedirectResponse('/login')
    # List files in S3 for this user (files are stored as user/filename)
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
    """
    Handle file upload:
    - Upload file to S3 under user's folder (user/filename)
    """
    if not user:
        return RedirectResponse('/login')
    s3_key = f"{user}/{file.filename}"
    s3_client.upload_fileobj(file.file, S3_BUCKET, s3_key)
    return RedirectResponse(f'/profile?user={user}', status_code=302)

@app.post('/send_message')
def send_message(request: Request):
    """
    Demo endpoint for sending a message (not implemented).
    """
    print("Message sent! (This is just a demo)")
    return RedirectResponse('/profile', status_code=302)

@app.get('/download/{filename}')
def download_file(filename: str, user: str = None):
    """
    Download a file from S3 for the user.
    - Streams the file from S3 to the browser
    """
    if not user:
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

# =====================
# MAIN ENTRY POINT
# =====================
if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 