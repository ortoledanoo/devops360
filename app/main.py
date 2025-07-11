"""
Main entry point for the DevOps360 application.

- Initializes the FastAPI app instance
- Mounts static files and sets up Jinja2 templates
- Loads routers modulesfor main authentication and profile management
- Defines the home page route
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import auth, profile

# Create the FastAPI application instance
app = FastAPI()

# Mount the 'static' directory to serve CSS, JS, and image files
app.mount('/static', StaticFiles(directory='app/static'), name='static')

# Set up Jinja2 templates for rendering HTML pages
templates = Jinja2Templates(directory='app/templates')

# Include authentication and profile routers (diffrent modules /routes path)
app.include_router(auth.router)
app.include_router(profile.router)

@app.get('/')
def home(request: Request):
    """
    Home page route.
    Renders the home.html template, which provides links to login and register.
    """
    return templates.TemplateResponse('home.html', {'request': request})