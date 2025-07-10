import boto3
from app.config import AWS_REGION, DDB_TABLE

ddb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = ddb.Table(DDB_TABLE)

def put_user_profile(user_profile: dict):
    table.put_item(Item=user_profile)

def get_user_profile(user_id: str):
    resp = table.get_item(Key={'user_id': user_id})
    return resp.get('Item')
