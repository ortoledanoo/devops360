# DevOps360 – Modern DevOps Practice App

## 1. Project Overview & File Structure

This is a modern, full-stack web app for DevOps practice, built with FastAPI (Python) and a hi-tech HTML/CSS frontend. It demonstrates authentication, file uploads, profile management, and AWS SNS integration (mocked).

### What Each File/Folder Does

- **main.py**: The main FastAPI app. Handles routing, user sessions, file upload/download/preview, profile management, and integrates all modules.
- **auth.py**: Handles user registration, login, 2FA (mocked), and session management. Stores user data in memory (dictionary).
- **models.py**: Pydantic models for user data validation (registration, login, profile info).
- **sns.py**: Mock integration for AWS SNS (sending messages). In production, this would use boto3 to send real SMS or notifications.
- **storage.py**: Handles file uploads. Files are saved to the `uploads/` directory, organized by username.
- **templates/**: Contains all HTML templates (login, register, profile, edit profile, file previews) rendered by FastAPI using Jinja2.
- **static/style.css**: Modern, hi-tech CSS for all pages.
- **uploads/**: Where all uploaded files are stored, organized by user. (In production, this would be S3.)
- **README.md**: This documentation.
- **venv/**: Python virtual environment (not included in repo).

### Where Data is Stored
- **User Data**: In-memory Python dictionary (for demo only; not persistent!).
- **Uploaded Files**: Saved in `uploads/<username>/`.
- **Logs**: Currently, logs are printed to the console. For production, configure FastAPI logging to write to files or a logging service.
- **Profile Edits**: Changes are kept in memory (lost on restart). In production, use a database.

---

## 2. AWS Roadmap: Deploying DevOps360 as a Real Microservices App

### Step-by-Step AWS Architecture

1. **Containerize the App**
   - Use Docker to containerize the FastAPI app.

2. **Store Images**
   - Push Docker images to Amazon ECR (Elastic Container Registry).

3. **Secrets Management**
   - Store sensitive data (DB passwords, API keys, etc.) in AWS Secrets Manager.

4. **User Data & State**
   - Use Amazon RDS (PostgreSQL/MySQL) or DynamoDB for persistent user data.
   - Store uploaded files in Amazon S3 (each user gets a folder/prefix).

5. **Microservices & Orchestration**
   - Deploy the app as a microservice in Amazon EKS (Elastic Kubernetes Service).
   - Use multiple pods/services for auth, file storage, user profile, etc. (split main.py into microservices as you scale).

6. **Networking & Security**
   - Use AWS Certificate Manager (ACM) for SSL/TLS certificates.
   - Use AWS ALB (Application Load Balancer) for routing and HTTPS termination.
   - Use IAM roles for service permissions (S3, SNS, Secrets, etc.).

7. **Notifications**
   - Integrate real AWS SNS for sending SMS or email notifications.

8. **Monitoring & Logging**
   - Use Amazon CloudWatch for logs and metrics.
   - Set up alerts for errors, high latency, etc.

9. **CI/CD**
   - Use AWS CodePipeline or GitHub Actions to automate build, test, and deploy.

### Example AWS Services Used
- **EKS**: Kubernetes cluster for running containers
- **ECR**: Container image storage
- **S3**: File storage (uploads)
- **RDS/DynamoDB**: User and app data
- **SNS**: Notifications (SMS/email)
- **Secrets Manager**: Store secrets
- **ACM**: SSL certificates
- **ALB**: Load balancing and HTTPS
- **CloudWatch**: Logging and monitoring
- **IAM**: Permissions and security

---

## 3. Infrastructure as Code (Terraform Roadmap)

To automate and manage all AWS resources, use Terraform. Here's a high-level plan:

1. **Set Up Terraform Project**
   - Create a `main.tf`, `variables.tf`, and `outputs.tf`.
   - Configure AWS provider and backend (S3 + DynamoDB for state).

2. **Define Resources**
   - **ECR**: `aws_ecr_repository` for Docker images
   - **EKS**: `aws_eks_cluster`, node groups, IAM roles
   - **S3**: `aws_s3_bucket` for uploads
   - **RDS/DynamoDB**: `aws_db_instance` or `aws_dynamodb_table`
   - **SNS**: `aws_sns_topic`, `aws_sns_topic_subscription`
   - **Secrets Manager**: `aws_secretsmanager_secret`
   - **ACM**: `aws_acm_certificate`
   - **ALB**: `aws_lb`, `aws_lb_target_group`, `aws_lb_listener`
   - **IAM**: `aws_iam_role`, `aws_iam_policy`
   - **CloudWatch**: `aws_cloudwatch_log_group`

3. **Networking**
   - VPC, subnets, security groups, route tables

4. **Outputs**
   - Export endpoints, ARNs, and other useful info

5. **CI/CD Integration**
   - Use Terraform Cloud or GitHub Actions for automated deployments

### Example Directory Structure
```
infra/
  main.tf
  variables.tf
  outputs.tf
  modules/
    eks/
    s3/
    rds/
    sns/
    ...
```

---

## Next Steps for You
- Try running and modifying the app locally
- Practice containerizing it with Docker
- Start writing Terraform for a simple resource (e.g., S3 bucket)
- Gradually build out the AWS infrastructure as described above
- When ready, split the app into microservices and deploy to EKS

**You're on your way to mastering DevOps in the cloud! 🚀** 