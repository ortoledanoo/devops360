# DevOps360 – FastAPI + AWS DynamoDB/S3 Example

## 🚀 What is this project?
This is a simple, modern web app built with **FastAPI** (Python) that lets you:
- Register and log in users
- Store user data (including address, zip code, and profile photo) in **DynamoDB**
- Upload and download files to/from **S3**
- See your profile and uploaded files

It's designed for beginners and DevOps learners who want to see how Python, AWS, and web apps work together.

---

## 🗂️ Project Structure
```
Devops360/
├── main.py              # The main FastAPI app (all logic here, with detailed comments)
├── templates/           # HTML pages (Jinja2)
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── static/
│   └── style.css        # Modern CSS for all pages
├── README.md            # This file
└── .gitignore           # Git ignore rules
```

---

## 🛠️ Prerequisites
- Python 3.10+
- AWS account
- AWS CLI configured (`aws configure`)
- DynamoDB table: `my-app-db` (partition key: `user_id`, type: String)
- S3 bucket: `my-s3-real-bucket` (in the same region as your DynamoDB table)
- Your AWS credentials must have access to both DynamoDB and S3

---

## ⚙️ Setup & Run
1. **Clone the repo and enter the directory**
2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn jinja2 python-multipart boto3
   ```
4. **Set your AWS region in `main.py`:**
   ```python
   AWS_REGION = 'us-east-1'  # Change to your region if needed
   ```
5. **Run the app:**
   ```bash
   python main.py
   ```
6. **Open your browser:**
   - Go to [http://localhost:8000](http://localhost:8000)

---

## 📝 How it Works (with Comments)

### 1. **AWS Setup in Code**
- The app uses `boto3` to connect to DynamoDB and S3.
- You must set the correct AWS region in `main.py`:
  ```python
  AWS_REGION = 'us-east-1'  # <-- Set this to your region
  s3_client = boto3.client('s3', region_name=AWS_REGION)
  ddb = boto3.resource('dynamodb', region_name=AWS_REGION)
  table = ddb.Table('my-app-db')
  ```

### 2. **User Registration**
- Checks if the username exists in DynamoDB.
- If a profile photo is uploaded, it is saved to S3 and the public URL is stored in DynamoDB.
- All user data (username, email, password, address, zip code, photo URL) is saved as a single item in DynamoDB.

### 3. **Login**
- Fetches the user from DynamoDB by `user_id`.
- Checks the password (plain text for demo; in real apps, always hash passwords!).
- If correct, redirects to the profile page.

### 4. **Profile Page**
- Loads user data from DynamoDB.
- Lists all files in S3 under the user's folder (e.g., `username/filename.txt`).
- Shows address, zip code, and profile photo (if present).

### 5. **File Upload**
- Lets the user upload files to S3 (stored as `username/filename`).
- Uploaded files are listed on the profile page.

### 6. **File Download**
- Streams files from S3 to the user's browser.
- Only allows download if the user is logged in.

---

## 🧑‍💻 Code Walkthrough (main.py)
- **AWS_REGION**: Set this to match your AWS resources.
- **S3_BUCKET**: Name of your S3 bucket.
- **DDB_TABLE**: Name of your DynamoDB table.
- **s3_client/ddb/table**: boto3 clients for AWS services.
- **@app.get('/register')**: Shows the registration form.
- **@app.post('/register')**: Handles registration, uploads photo to S3, saves user to DynamoDB.
- **@app.get('/login')**: Shows the login form.
- **@app.post('/login')**: Checks credentials against DynamoDB.
- **@app.get('/profile')**: Loads user data and file list from AWS.
- **@app.post('/upload')**: Uploads a file to S3 under the user's folder.
- **@app.get('/download/{filename}')**: Streams a file from S3 for download.

---

## 🏗️ How to Extend This Project
- Add password hashing (use `bcrypt` or `passlib`)
- Add user sessions (use `fastapi-login` or `fastapi-users`)
- Add email verification (use AWS SES)
- Add file preview (images, text)
- Add user profile editing
- Add admin features
- Deploy to AWS (ECS, EKS, or Lambda)
- Use Terraform or AWS CDK for infrastructure as code

---

## 🐛 Troubleshooting
- **ResourceNotFoundException**: Make sure your DynamoDB table and S3 bucket exist in the correct region.
- **AccessDenied**: Check your AWS credentials and permissions.
- **File upload issues**: Make sure your S3 bucket allows uploads and your IAM user/role has `s3:PutObject` permission.
- **Profile photo not showing**: Make sure your S3 bucket allows public read or use signed URLs.

---

## 💡 Tips for Beginners
- Read the comments in `main.py` – they explain every step.
- Try changing the code and see what happens!
- Use the AWS Console to view your DynamoDB table and S3 bucket.
- Always use environment variables or AWS Secrets Manager for real credentials (never hardcode in production).

---

## 📚 Useful Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [DynamoDB Docs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)
- [S3 Docs](https://docs.aws.amazon.com/s3/index.html)
- [AWS Free Tier](https://aws.amazon.com/free/)

---

## S3 Bucket Policy for Public Profile Photos

To allow users' profile photos to be publicly viewable (while keeping all other files private), add the following bucket policy to your S3 bucket:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicReadProfilePhotos",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-s3-real-bucket/profile_photos/*"
    }
  ]
}
```

- Replace `my-s3-real-bucket` with your actual bucket name if different.
- This policy allows public read access **only** to files in the `profile_photos/` directory.
- All other files in the bucket remain private by default.

**Note:** You must also turn OFF "Block all public access" for your bucket in the AWS S3 console for this policy to take effect.

---

**Happy learning and building! 🚀** 