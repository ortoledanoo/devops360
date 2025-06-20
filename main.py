from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# Create the FastAPI app
app = FastAPI()

# Serve static files (CSS) from the 'static' folder
app.mount('/static', StaticFiles(directory='static'), name='static')

# Set up templates (HTML files) from the 'templates' folder
templates = Jinja2Templates(directory='templates')

# Simple in-memory storage for users (in real apps, you'd use a database)
users = {}

# Simple in-memory storage for uploaded files info
user_files = {}

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
    # Check if username already exists
    if username in users:
        return templates.TemplateResponse('register.html', {
            'request': request, 
            'error': 'Username already exists!'
        })
    
    # Store user info (in real apps, you'd hash the password)
    users[username] = {
        'username': username,
        'email': email,
        'password': password  # In real apps, NEVER store passwords like this!
    }
    
    # Redirect to login page
    return RedirectResponse('/login', status_code=302)

@app.get('/login')
def login_page(request: Request):
    """Show the login page"""
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/login')
def login_user(request: Request, username: str = Form(), password: str = Form()):
    """Handle user login"""
    # Check if user exists and password matches
    if username in users and users[username]['password'] == password:
        # In real apps, you'd set a proper session cookie
        return RedirectResponse('/profile', status_code=302)
    else:
        return templates.TemplateResponse('login.html', {
            'request': request, 
            'error': 'Wrong username or password!'
        })

@app.get('/profile')
def profile_page(request: Request):
    """Show the user profile page"""
    # For simplicity, we'll show a demo user
    # In real apps, you'd get the user from the session
    demo_user = {
        'username': 'demo_user',
        'email': 'demo@example.com'
    }
    
    # Get user's files (if any)
    user_files_list = user_files.get(demo_user['username'], [])
    
    return templates.TemplateResponse('profile.html', {
        'request': request,
        'user': demo_user,
        'files': user_files_list
    })

@app.post('/upload')
def upload_file(request: Request, file: str = Form()):
    """Handle file upload (simplified - just stores filename)"""
    # In real apps, you'd actually save the file
    demo_user = 'demo_user'
    
    if demo_user not in user_files:
        user_files[demo_user] = []
    
    user_files[demo_user].append(file)
    
    return RedirectResponse('/profile', status_code=302)

@app.post('/send_message')
def send_message(request: Request):
    """Handle sending a message (simplified)"""
    # In real apps, you'd integrate with AWS SNS
    print("Message sent! (This is just a demo)")
    return RedirectResponse('/profile', status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 