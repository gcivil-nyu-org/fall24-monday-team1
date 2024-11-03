import boto3
import os
from botocore.exceptions import ClientError
from django.conf import settings
import time

def create_dynamodb_tables():
    dynamodb = boto3.client(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    
    tables_to_create = {
        'friend_requests': {
            'KeySchema': [
                {'AttributeName': 'to_user', 'KeyType': 'HASH'},
                {'AttributeName': 'from_user', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'to_user', 'AttributeType': 'S'},
                {'AttributeName': 'from_user', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'from_user-index',
                    'KeySchema': [
                        {'AttributeName': 'from_user', 'KeyType': 'HASH'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        },
        'user_friends': {
            'KeySchema': [
                {'AttributeName': 'username', 'KeyType': 'HASH'},
                {'AttributeName': 'friend', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'username', 'AttributeType': 'S'},
                {'AttributeName': 'friend', 'AttributeType': 'S'}
            ],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    }

    for table_name, table_config in tables_to_create.items():
        try:
            # Check if table exists
            dynamodb.describe_table(TableName=table_name)
            print(f"Table {table_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table if it doesn't exist
                print(f"Creating table {table_name}...")
                dynamodb.create_table(
                    TableName=table_name,
                    **table_config
                )
                # Wait for table to be created
                waiter = dynamodb.get_waiter('table_exists')
                waiter.wait(TableName=table_name)
                print(f"Table {table_name} created successfully")
            else:
                print(f"Error checking/creating table {table_name}: {e}")