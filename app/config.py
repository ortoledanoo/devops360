"""
Configuration module for DevOps360 FastAPI application.

Loads all environment variables required for AWS and Cognito integration.
This centralizes configuration for easy management and cloud-native best practices.
"""

import os

# AWS region to use for all AWS service clients
AWS_REGION = os.environ.get('AWS_REGION', 'il-central-1')

# S3 bucket name for storing user files and profile photos
S3_BUCKET = os.environ['S3_BUCKET_NAME']

# DynamoDB table name for storing user profile data
DDB_TABLE = os.environ['DYNAMODB_TABLE_NAME']

# Cognito User Pool ID for authentication
COGNITO_USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID']

# Cognito region (usually same as AWS_REGION)
COGNITO_REGION = AWS_REGION

# Cognito App Client ID for authentication
COGNITO_APP_CLIENT_ID = os.environ['COGNITO_USER_POOL_CLIENT_ID']

# URL to fetch Cognito JWKS (public keys) for JWT verification
COGNITO_JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
