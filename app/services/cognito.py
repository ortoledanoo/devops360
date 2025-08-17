import boto3
import json
import hmac
import hashlib
import base64
from jose import jwt
import requests
from botocore.exceptions import ClientError
from app.config import AWS_REGION, COGNITO_USER_POOL_ID, COGNITO_REGION, COGNITO_APP_CLIENT_ID, COGNITO_JWKS_URL

# --- Secrets Manager Function Integration ---
def get_secret(secret_name, region_name):
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
    print(f"INFO: Attempting to load secret 'devops360/cognito' from region {AWS_REGION}")
    cognito_secrets = get_secret("devops360/cognito", AWS_REGION)
    COGNITO_APP_CLIENT_SECRET = cognito_secrets.get('COGNITO_APP_CLIENT_SECRET')
    if not COGNITO_APP_CLIENT_SECRET:
        raise ValueError("COGNITO_APP_CLIENT_SECRET not found in secret 'devops360/cognito'")
    print("INFO: Successfully loaded Cognito client secret from Secrets Manager")
except Exception as e:
    print(f"FATAL: Could not load secrets from AWS Secrets Manager. Error: {e}")
    print(f"FATAL: Error type: {type(e).__name__}")
    if hasattr(e, 'response'):
        print(f"FATAL: AWS Error Code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
        print(f"FATAL: AWS Error Message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
    COGNITO_APP_CLIENT_SECRET = None

_cognito_jwks = None
def get_cognito_jwks():
    global _cognito_jwks
    if _cognito_jwks is None:
        resp = requests.get(COGNITO_JWKS_URL)
        resp.raise_for_status()
        _cognito_jwks = resp.json()
    return _cognito_jwks

def verify_cognito_token(token):
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
def get_secret_hash(username: str) -> str:
    print(f"DEBUG: COGNITO_APP_CLIENT_SECRET is {'available' if COGNITO_APP_CLIENT_SECRET else 'None'}")
    print(f"DEBUG: Username: {username}")
    print(f"DEBUG: Client ID: {COGNITO_APP_CLIENT_ID}")
    
    message = username + COGNITO_APP_CLIENT_ID
    print(f"DEBUG: Message for HMAC: {message}")
    
    if not COGNITO_APP_CLIENT_SECRET:
        raise ValueError("COGNITO_APP_CLIENT_SECRET is None or empty")
    
    dig = hmac.new(
        str(COGNITO_APP_CLIENT_SECRET).encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    secret_hash = base64.b64encode(dig).decode()
    print(f"DEBUG: Generated SecretHash: {secret_hash}")
    return secret_hash

cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

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
