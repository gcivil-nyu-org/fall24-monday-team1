import boto3
import os
from botocore.exceptions import ClientError
from django.conf import settings
import time

# def create_dynamodb_tables():
#     dynamodb = boto3.resource(
#         'dynamodb',
#         aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
#         aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
#         region_name='us-east-1'
#     )

#     # Create friend_requests table with GSI
#     try:
#         dynamodb.create_table(
#             TableName='friend_requests',
#             KeySchema=[
#                 {'AttributeName': 'to_user', 'KeyType': 'HASH'},
#                 {'AttributeName': 'from_user', 'KeyType': 'RANGE'}
#             ],
#             AttributeDefinitions=[
#                 {'AttributeName': 'to_user', 'AttributeType': 'S'},
#                 {'AttributeName': 'from_user', 'AttributeType': 'S'}
#             ],
#             GlobalSecondaryIndexes=[
#                 {
#                     'IndexName': 'from_user-index',
#                     'KeySchema': [
#                         {'AttributeName': 'from_user', 'KeyType': 'HASH'},
#                     ],
#                     'Projection': {
#                         'ProjectionType': 'ALL'
#                     },
#                     'ProvisionedThroughput': {
#                         'ReadCapacityUnits': 5,
#                         'WriteCapacityUnits': 5
#                     }
#                 }
#             ],
#             ProvisionedThroughput={
#                 'ReadCapacityUnits': 5,
#                 'WriteCapacityUnits': 5
#             }
#         )
#         print("Created friend_requests table")

#         # Create user_friends table
#         dynamodb.create_table(
#             TableName='user_friends',
#             KeySchema=[
#                 {'AttributeName': 'username', 'KeyType': 'HASH'},
#                 {'AttributeName': 'friend', 'KeyType': 'RANGE'}
#             ],
#             AttributeDefinitions=[
#                 {'AttributeName': 'username', 'AttributeType': 'S'},
#                 {'AttributeName': 'friend', 'AttributeType': 'S'}
#             ],
#             ProvisionedThroughput={
#                 'ReadCapacityUnits': 5,
#                 'WriteCapacityUnits': 5
#             }
#         )
#         print("Created user_friends table")

#     except Exception as e:
#         print(f"Error creating tables: {e}")