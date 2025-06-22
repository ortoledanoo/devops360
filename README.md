# DevOps360 – FastAPI + AWS Cognito, S3, DynamoDB & Secrets Manager

## 🚀 What is this project?
This is a modern, secure web application built with **FastAPI** that demonstrates a complete user authentication and profile management lifecycle using a suite of AWS services. It's an excellent reference for learning how to integrate Python web apps with a secure, production-ready AWS backend.

### Features:
-   **Secure User Authentication with AWS Cognito:**
    -   User registration with email/phone confirmation.
    -   Secure login with Cognito handling all password management.
    -   Cookie-based session management for a seamless user experience.
    -   Protected endpoints that require a valid login session.
    -   Secure logout functionality.
-   **Secret Management with AWS Secrets Manager:**
    -   No hardcoded credentials. The Cognito client secret is fetched securely at startup.
-   **File Storage with Amazon S3:**
    -   Users can upload profile photos and other files to a dedicated S3 bucket.
-   **Profile Data Storage with Amazon DynamoDB:**
    -   Stores additional user profile information (like address) that is not part of the core Cognito attributes.

---

## 🏗️ Architecture Overview

1.  **Frontend:** The user interacts with HTML pages rendered by FastAPI's Jinja2 templating engine.
2.  **Backend (FastAPI):** The Python web server that handles all API requests.
3.  **Authentication (AWS Cognito):** Handles all user sign-up, sign-in, and confirmation flows. FastAPI communicates with Cognito via `boto3`.
4.  **Secrets (AWS Secrets Manager):** The FastAPI application fetches the Cognito client secret from Secrets Manager on startup.
5.  **Database (Amazon DynamoDB):** Stores non-sensitive, supplementary user profile data.
6.  **File Storage (Amazon S3):** Used for storing user-uploaded profile pictures and other files.

---

## 🛠️ Prerequisites
-   Python 3.10+
-   An AWS account with the [AWS CLI configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
-   Your IAM user/role must have permissions for: **Cognito, S3, DynamoDB, and Secrets Manager**.

### AWS Resource Setup:
1.  **AWS Cognito User Pool:**
    -   Create a User Pool.
    -   In your App Client settings, ensure the **"USER_PASSWORD_AUTH"** flow is enabled.
2.  **Amazon S3 Bucket:**
    -   Create a new S3 bucket in the same region as your app.
3.  **Amazon DynamoDB Table:**
    -   Create a new DynamoDB table with `user_id` (String) as the partition key.
4.  **AWS Secrets Manager Secret:**
    -   Create a new secret with the name `devops360/cognito`.
    -   Store it as a key/value pair:
        -   **Key:** `COGNITO_APP_CLIENT_SECRET`
        -   **Value:** Your Cognito App Client's secret value.

---

## ⚙️ Setup & Run
1.  **Clone the repo and enter the directory.**
2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **(Optional) Update configuration in `main.py`:**
    -   If your AWS resources have different names or are in a different region, update the configuration variables at the top of `main.py`.
5.  **Run the app:**
    ```bash
    python main.py
    ```
6.  **Open your browser** and go to [http://localhost:8000](http://localhost:8000).

---

## 📝 How it Works

#### Registration Flow
1.  A new user fills out the registration form.
2.  The `/register` endpoint calls Cognito's `sign_up` function.
3.  Cognito creates the user in an "UNCONFIRMED" state and sends a confirmation code via email/SMS.
4.  The user is redirected to the `/confirm` page.

#### Confirmation Flow
1.  The user enters their username and the confirmation code.
2.  The `/confirm` endpoint calls Cognito's `confirm_sign_up` function.
3.  If the code is valid, the user's status is set to "CONFIRMED".

#### Login Flow
1.  The user submits their username and password.
2.  The `/login` endpoint calls Cognito's `initiate_auth` function.
3.  If successful, Cognito returns JWT tokens.
4.  The server sets the `access_token` in a secure, `httponly` cookie and redirects the user to their profile.

#### Protected Routes & Sessions
-   Endpoints like `/profile` are protected by a FastAPI dependency (`require_cognito_token`).
-   This dependency checks for the `cognito_token` cookie on every request. If the cookie is present and contains a valid JWT, access is granted. Otherwise, it's denied.

#### Logout Flow
-   Clicking the "Logout" button sends a request to the `/logout` endpoint.
-   This endpoint clears the `cognito_token` cookie and redirects the user to the home page.

---

## 📚 Useful Links
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
-   [AWS Cognito Docs](https://docs.aws.amazon.com/cognito/index.html)
-   [AWS Secrets Manager Docs](https://docs.aws.amazon.com/secretsmanager/index.html)

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