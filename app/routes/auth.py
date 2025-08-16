from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.cognito import cognito_client, get_secret_hash, cognito_error_message
from app.services.dynamodb import put_user_profile
from app.services.s3 import upload_fileobj
from app.config import COGNITO_APP_CLIENT_ID
import uuid

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get('/register')
def register_page(request: Request):
    return templates.TemplateResponse('register.html', {'request': request})

@router.post('/register')
def cognito_register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    address: str = Form(...),
    phone_number: str = Form(...),
    profile_photo: UploadFile = File(None)
):
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
        from app.services.cognito import COGNITO_APP_CLIENT_SECRET
        print(f"DEBUG: COGNITO_APP_CLIENT_SECRET is {'available' if COGNITO_APP_CLIENT_SECRET else 'None'}")
        if COGNITO_APP_CLIENT_SECRET:
            params['SecretHash'] = get_secret_hash(username)
        else:
            print("WARNING: No Cognito client secret available - registration may fail")
        
        print(f"DEBUG: Attempting Cognito sign_up for user: {username}")
        cognito_client.sign_up(**params)
        print(f"INFO: Successfully registered user: {username}")
    except Exception as e:
        print(f"ERROR: Registration failed for user {username}: {e}")
        print(f"ERROR: Exception type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"ERROR: AWS Error Code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
            print(f"ERROR: AWS Error Message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        return templates.TemplateResponse('register.html', {
            'request': request,
            'error': cognito_error_message(e)
        })
    photo_url = ''
    if profile_photo:
        photo_key = f"profile_photos/{username}_{uuid.uuid4()}_{profile_photo.filename}"
        upload_fileobj(profile_photo.file, photo_key)
        from app.config import S3_BUCKET
        photo_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{photo_key}"
    put_user_profile({
        'user_id': username,
        'email': email,
        'address': address,
        'phone_number': phone_number,
        'profile_photo': photo_url
    })
    return RedirectResponse('/confirm', status_code=302)

@router.get('/login')
def login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

@router.post('/login')
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    auth_params = {
        'USERNAME': username,
        'PASSWORD': password
    }
    from app.services.cognito import COGNITO_APP_CLIENT_SECRET
    if COGNITO_APP_CLIENT_SECRET:
        auth_params['SECRET_HASH'] = get_secret_hash(username)
    try:
        resp = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters=auth_params,
            ClientId=COGNITO_APP_CLIENT_ID
        )
        access_token = resp['AuthenticationResult']['AccessToken']
        response = RedirectResponse(f'/profile?user={username}', status_code=302)
        response.set_cookie(key="cognito_token", value=access_token, httponly=True)
        return response
    except Exception as e:
        return templates.TemplateResponse('login.html', {
            'request': request,
            'error': cognito_error_message(e)
        })

@router.get('/logout')
def logout():
    response = RedirectResponse('/', status_code=302)
    response.delete_cookie("cognito_token")
    return response

@router.get('/confirm')
def confirm_page(request: Request):
    return templates.TemplateResponse('confirm.html', {'request': request})

@router.post('/confirm')
def confirm_user(request: Request, username: str = Form(...), code: str = Form(...)):
    try:
        params = {
            'ClientId': COGNITO_APP_CLIENT_ID,
            'Username': username,
            'ConfirmationCode': code
        }
        from app.services.cognito import COGNITO_APP_CLIENT_SECRET
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
