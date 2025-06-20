# DevOps360 – Simple Web App for Learning DevOps

## 🎯 What This Is

This is a **simple web application** built to help you understand basic web development concepts before diving into DevOps. It's designed to be easy to understand for beginners.

## 📁 Project Structure (Simplified)

```
Devops360/
├── main.py              # The main application (everything in one file!)
├── templates/           # HTML pages
│   ├── home.html       # Welcome page
│   ├── login.html      # Login form
│   ├── register.html   # Registration form
│   └── profile.html    # User profile page
├── static/
│   └── style.css       # Styling for all pages
├── uploads/            # Where files would be stored (not used in demo)
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## 🚀 How to Run

1. **Install Python** (if you haven't already)
2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn jinja2 python-multipart
   ```
4. **Run the app:**
   ```bash
   python main.py
   ```
5. **Open your browser** and go to: `http://localhost:8000`

## 📖 What Each File Does

### `main.py` - The Main Application
- **What it is:** A single Python file that contains everything
- **What it does:** 
  - Creates a web server
  - Handles user registration and login
  - Shows different pages (home, login, register, profile)
  - Stores user data in memory (simple dictionary)
  - Handles file uploads (demo only)

### `templates/` - HTML Pages
- **home.html:** Welcome page with links to login/register
- **login.html:** Form where users enter username/password
- **register.html:** Form where new users create accounts
- **profile.html:** Shows user info and lets them upload files

### `static/style.css` - Styling
- Makes the app look modern and professional
- Uses dark theme with blue/green colors

## 🔍 Key Concepts to Understand

### 1. **Web Routes** (in `main.py`)
```python
@app.get('/')           # When someone visits the homepage
@app.post('/login')     # When someone submits the login form
@app.get('/profile')    # When someone visits their profile
```

### 2. **Templates** (HTML + Python)
```html
<!-- In HTML -->
<h2>Welcome, {{ user.username }}!</h2>

<!-- This shows the username from Python -->
```

### 3. **Forms** (How data moves around)
```python
# When user submits a form, we get the data:
username = Form()  # Gets the username from the form
password = Form()  # Gets the password from the form
```

### 4. **Data Storage** (Simple version)
```python
# Store users in a dictionary (in real apps, you'd use a database)
users = {
    'john': {'username': 'john', 'email': 'john@example.com', 'password': '123'}
}
```

## 🎯 What You Can Do With This App

1. **Register** a new account
2. **Login** with your credentials
3. **View** your profile
4. **Upload** files (demo - just enter a filename)
5. **Send messages** (demo - just prints to console)

## 🔧 How to Modify and Learn

### Try These Changes:

1. **Add a new page:**
   ```python
   @app.get('/about')
   def about_page(request: Request):
       return templates.TemplateResponse('about.html', {'request': request})
   ```

2. **Add a new field to registration:**
   ```python
   # In main.py, add phone = Form() to the register function
   # In register.html, add <input type="text" name="phone">
   ```

3. **Change the styling:**
   - Edit `static/style.css` to change colors, fonts, etc.

4. **Add more user data:**
   - Modify the `users` dictionary to store more information

## 🚀 Next Steps for DevOps

Once you understand this basic app, you can:

1. **Add a real database** (PostgreSQL, MySQL)
2. **Containerize** with Docker
3. **Deploy** to AWS/Google Cloud/Azure
4. **Add monitoring** and logging
5. **Set up CI/CD** pipelines
6. **Use Infrastructure as Code** (Terraform)

## 💡 Tips for Beginners

- **Start small:** Don't try to understand everything at once
- **Experiment:** Change things and see what happens
- **Read the comments:** They explain what each part does
- **Ask questions:** If something doesn't make sense, look it up!

## 🐛 Common Issues

- **"Module not found"**: Make sure you installed the dependencies
- **"Port already in use"**: Try a different port or stop other apps
- **"Page not found"**: Check that the URL is correct

---

**Remember:** This is a learning tool. In real applications, you'd never store passwords in plain text or use in-memory storage. But this helps you understand the basics before moving to more complex topics!

Happy learning! 🎉 