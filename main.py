# =====================
# DevOps360 Main Application
#
# This FastAPI app demonstrates user authentication and profile management
# using AWS Cognito for secure login/registration and DynamoDB/S3 for storing
# additional user data and files. All comments are detailed for easy review.
# =====================

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import boto3
import io
import uuid
from jose import jwt
import requests
import hmac
import hashlib
import base64
import json
from botocore.exceptions import ClientError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# =====================
# AWS CONFIGURATION
# =====================
# All configuration is now loaded from environment variables for cloud-native best practice.
AWS_REGION = os.environ.get('AWS_REGION', 'il-central-1')
S3_BUCKET = os.environ['S3_BUCKET_NAME']
DDB_TABLE = os.environ['DYNAMODB_TABLE_NAME']

# =====================
# FASTAPI APP SETUP
# =====================
app = FastAPI()

# Serve static files (CSS) from the 'static' folder
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up templates (HTML files) from the 'templates' folder
templates = Jinja2Templates(directory='templates')

# =====================
# AWS CLIENTS & SECRETS
# =====================
# Create AWS clients/resources with explicit region
s3_client = boto3.client('s3', region_name=AWS_REGION)
ddb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = ddb.Table(DDB_TABLE) # type: ignore

# --- Secrets Manager Function Integration ---
def get_secret(secret_name, region_name):
    """
    Retrieve a secret from AWS Secrets Manager.
    This function fetches and parses the JSON secret string.
    """
    session = boto3.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f"Error fetching secret '{secret_name}': {e}")
        raise e
    
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# --- Use get_secret function to load Cognito secrets ---
try:
    cognito_secrets = get_secret("devops360/cognito", AWS_REGION)
    COGNITO_APP_CLIENT_SECRET = cognito_secrets.get('COGNITO_APP_CLIENT_SECRET')
    if not COGNITO_APP_CLIENT_SECRET:
        raise ValueError("COGNITO_APP_CLIENT_SECRET not found in secret 'devops360/cognito'")
except Exception as e:
    print(f"FATAL: Could not load secrets from AWS Secrets Manager. {e}")
    COGNITO_APP_CLIENT_SECRET = None # App will fail if secret is not loaded

# =====================
# COGNITO CONFIGURATION
# =====================
# All authentication is handled by Cognito (not DynamoDB)
COGNITO_USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID']
COGNITO_REGION = AWS_REGION
COGNITO_APP_CLIENT_ID = os.environ['COGNITO_USER_POOL_CLIENT_ID']
# COGNITO_APP_CLIENT_SECRET is now loaded from AWS Secrets Manager
COGNITO_JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

# Helper to get Cognito JWKS (public keys for token verification)
_cognito_jwks = None
def get_cognito_jwks():
    """
    Download and cache the Cognito JWKS (public keys) for verifying JWT tokens.
    """
    global _cognito_jwks
    if _cognito_jwks is None:
        resp = requests.get(COGNITO_JWKS_URL)
        resp.raise_for_status()
        _cognito_jwks = resp.json()
    return _cognito_jwks

def verify_cognito_token(token):
    """
    Verify a JWT token issued by Cognito using the JWKS.
    Returns the decoded token if valid, or None if invalid.
    """
    jwks = get_cognito_jwks()
    try:
        header = jwt.get_unverified_header(token)
        key = next(k for k in jwks['keys'] if k['kid'] == header['kid'])
        return jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=COGNITO_APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
        )
    except Exception as e:
        print(f"Cognito token verification failed: {e}")
        return None

# Helper to calculate Cognito SECRET_HASH for a username
def get_secret_hash(username: str) -> str:
    """
    Calculate the Cognito SECRET_HASH for a given username.
    """
    message = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(
        str(COGNITO_APP_CLIENT_SECRET).encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

# Create a single Cognito client to reuse
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

# Helper to map Cognito exceptions to user-friendly error messages
def cognito_error_message(e):
    if hasattr(e, 'response') and 'Error' in e.response:
        code = e.response['Error'].get('Code', '')
        if code == 'NotAuthorizedException':
            return 'Incorrect username or password!'
        elif code == 'UserNotFoundException':
            return 'User does not exist!'
        elif code == 'UserNotConfirmedException':
            return 'User not confirmed. Please check your email or phone for the confirmation code.'
        elif code == 'UsernameExistsException':
            return 'A user with this username already exists!'
        elif code == 'ExpiredCodeException':
            return 'Confirmation code expired. Please request a new one.'
        elif code == 'CodeMismatchException':
            return 'Invalid confirmation code.'
    return f'Error: {e}'

# FastAPI dependency to require a valid Cognito JWT token
security = HTTPBearer(auto_error=False)

def require_cognito_token(request: Request, auth: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    FastAPI dependency to protect endpoints.
    - Requires a valid Cognito JWT token from either a cookie or Authorization header.
    - Returns the decoded token if valid, otherwise raises an exception.
    """
    token = request.cookies.get("cognito_token")
    if not token and auth:
        token = auth.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    decoded = verify_cognito_token(token)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )
    return decoded

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
    Show the registration form for new users.
    """
    return templates.TemplateResponse('register.html', {'request': request})

@app.post('/register')
def cognito_register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    address: str = Form(...),
    phone_number: str = Form(...),
    profile_photo: UploadFile = File(None)
):
    """
    Register a new user in Cognito (username, email, phone_number).
    - Registers user in Cognito (handles authentication, confirmation, etc)
    - Uploads profile photo to S3 (optional)
    - Stores user profile info (not password) in DynamoDB
    - Redirects to confirmation page after registration
    """
    try:
        params = {
            'ClientId': COGNITO_APP_CLIENT_ID,
            'Username': username,
            'Password': password,
            'UserAttributes': [
                {'Name': 'email', 'Value': email},
                {'Name': 'name', 'Value': username},
                {'Name': 'address', 'Value': address},
                {'Name': 'phone_number', 'Value': phone_number}
            ]
        }
        if COGNITO_APP_CLIENT_SECRET:
            params['SecretHash'] = get_secret_hash(username)
        cognito_client.sign_up(**params)
    except Exception as e:
        return templates.TemplateResponse('register.html', {
            'request': request,
            'error': cognito_error_message(e)
        })
    # Upload profile photo to S3 (optional)
    photo_url = ''
    if profile_photo:
        # Store photo in S3 under a unique key
        photo_key = f"profile_photos/{username}_{uuid.uuid4()}_{profile_photo.filename}"
        s3_client.upload_fileobj(profile_photo.file, S3_BUCKET, photo_key)
        photo_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{photo_key}"
        
    # Save user profile info (not password) in DynamoDB
    table.put_item(Item={
        'user_id': username,
        'email': email,
        'address': address,
        'phone_number': phone_number,
        'profile_photo': photo_url
    })
    # Redirect to confirmation page after successful registration
    return RedirectResponse('/confirm', status_code=302)

@app.get('/login')
def login_page(request: Request):
    """
    Show the login form for users.
    """
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/login')
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Authenticate user with Cognito.
    - If successful, sets a secure cookie with the auth token and redirects to profile page.
    - If failed, shows an error message.
    """
    auth_params = {
        'USERNAME': username,
        'PASSWORD': password
    }
    if COGNITO_APP_CLIENT_SECRET:
        auth_params['SECRET_HASH'] = get_secret_hash(username)
    try:
        resp = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters=auth_params,
            ClientId=COGNITO_APP_CLIENT_ID
        )
        # On success, create a redirect response and set the auth token in a secure cookie
        access_token = resp['AuthenticationResult']['AccessToken']
        response = RedirectResponse(f'/profile?user={username}', status_code=302)
        response.set_cookie(key="cognito_token", value=access_token, httponly=True)
        return response
    except Exception as e:
        return templates.TemplateResponse('login.html', {
            'request': request,
            'error': cognito_error_message(e)
        })

@app.get('/profile')
def profile_page(request: Request, user: Optional[str] = None, token_data: dict = Depends(require_cognito_token)):
    """
    Show the user's profile page.
    - Protected: requires a valid Cognito token from a cookie or Authorization header.
    - Loads user profile info from DynamoDB.
    - Lists files uploaded by the user from S3.
    """
    if not user:
        # If not logged in, redirect to login
        return RedirectResponse('/login')
    # Fetch user profile from DynamoDB
    resp = table.get_item(Key={'user_id': user})
    user_data = resp.get('Item')
    if not user_data:
        # User not found in DynamoDB
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
def upload_file(request: Request, user: str = Form(), file: UploadFile = File(...), token_data: dict = Depends(require_cognito_token)):
    """
    Handle file upload for a user.
    - Protected: requires a valid Cognito token from a cookie or Authorization header.
    - Uploads file to S3 under user's folder (user/filename).
    """
    if not user:
        return RedirectResponse('/login')
    s3_key = f"{user}/{file.filename}"
    s3_client.upload_fileobj(file.file, S3_BUCKET, s3_key)
    return RedirectResponse(f'/profile?user={user}', status_code=302)

@app.get('/logout')
def logout():
    """
    Log out the user by deleting the auth cookie and redirecting to the home page.
    """
    response = RedirectResponse('/', status_code=302)
    response.delete_cookie("cognito_token")
    return response

@app.post('/send_message')
def send_message(request: Request):
    """
    Demo endpoint for sending a message (not implemented).
    """
    print("Message sent! (This is just a demo)")
    return RedirectResponse('/profile', status_code=302)

@app.get('/download/{filename}')
def download_file(filename: str, user: Optional[str] = None):
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

@app.post('/cognito-login')
def cognito_login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticate user with AWS Cognito and return tokens if successful (API use).
    """
    auth_params = {
        'USERNAME': username,
        'PASSWORD': password
    }
    if COGNITO_APP_CLIENT_SECRET:
        auth_params['SECRET_HASH'] = get_secret_hash(username)
    try:
        resp = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters=auth_params,
            ClientId=COGNITO_APP_CLIENT_ID
        )
        return JSONResponse({
            'access_token': resp['AuthenticationResult']['AccessToken'],
            'id_token': resp['AuthenticationResult']['IdToken'],
            'refresh_token': resp['AuthenticationResult']['RefreshToken']
        })
    except Exception as e:
        return JSONResponse({'error': cognito_error_message(e)}, status_code=401)

@app.get('/confirm')
def confirm_page(request: Request):
    """
    Show the confirmation form for username and code.
    """
    return templates.TemplateResponse('confirm.html', {'request': request})

@app.post('/confirm')
def confirm_user(request: Request, username: str = Form(...), code: str = Form(...)):
    """
    Confirm a Cognito user with the code sent to their email or phone.
    - Uses the username (not email) for Cognito confirmation
    - Handles code mismatch, expired code, and other errors
    """
    try:
        params = {
            'ClientId': COGNITO_APP_CLIENT_ID,
            'Username': username,
            'ConfirmationCode': code
        }
        if COGNITO_APP_CLIENT_SECRET:
            params['SecretHash'] = get_secret_hash(username)
        cognito_client.confirm_sign_up(**params)
        return templates.TemplateResponse('confirm.html', {
            'request': request,
            'success': 'Your account has been confirmed! You can now log in.',
            'error': None
        })
    except Exception as e:
        return templates.TemplateResponse('confirm.html', {
            'request': request,
            'error': cognito_error_message(e),
            'success': None
        })

# =====================
# MAIN ENTRY POINT
# =====================
if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 