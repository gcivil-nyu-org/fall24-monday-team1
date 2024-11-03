from django.conf import settings
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime

class FriendRequest:
    @staticmethod
    def get_dynamodb_resource():
        return boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )

    @staticmethod
    def ensure_table_exists(table_name):
        from .utils import create_dynamodb_tables
        try:
            dynamodb = FriendRequest.get_dynamodb_resource()
            table = dynamodb.Table(table_name)
            table.table_status  # This will raise an exception if table doesn't exist
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                create_dynamodb_tables()
                # Try again after creating tables
                dynamodb = FriendRequest.get_dynamodb_resource()
                return dynamodb.Table(table_name)
            raise e
        

    @staticmethod
    def get_friend_requests_table():
        return FriendRequest.ensure_table_exists('friend_requests')

    @staticmethod
    def get_friends_table():
        return FriendRequest.ensure_table_exists('user_friends')

    @staticmethod
    def send_request(from_user, to_user):
        table = FriendRequest.get_friend_requests_table()
        try:
            table.put_item(
                Item={
                    'to_user': to_user,
                    'from_user': from_user,
                    'status': 'pending'
                }
            )
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    @staticmethod
    def get_pending_requests(user):
        table = FriendRequest.get_friend_requests_table()
        try:
            response = table.query(
                KeyConditionExpression='to_user = :user',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':user': user, ':status': 'pending'}
            )
            return response['Items']
        except ClientError as e:
            print(e.response['Error']['Message'])
            return []

    @staticmethod
    def accept_request(from_user, to_user):
        try:
            # Delete the request
            requests_table = FriendRequest.get_friend_requests_table()
            requests_table.delete_item(
                Key={'to_user': to_user, 'from_user': from_user}
            )
            
            # Add both users to each other's friends list
            friends_table = FriendRequest.get_friends_table()
            timestamp = str(datetime.now())
            
            # Add to first user's friends
            friends_table.put_item(
                Item={
                    'username': to_user,
                    'friend': from_user,
                    'created_at': timestamp
                }
            )
            
            # Add to second user's friends
            friends_table.put_item(
                Item={
                    'username': from_user,
                    'friend': to_user,
                    'created_at': timestamp
                }
            )
            return True
        except ClientError as e:
            print(f"Error accepting friend request: {e.response['Error']['Message']}")
            return False

    @staticmethod
    def reject_request(from_user, to_user):
        table = FriendRequest.get_friend_requests_table()
        try:
            table.delete_item(Key={'to_user': to_user, 'from_user': from_user})
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    @staticmethod
    def get_friends(username):
        table = FriendRequest.get_friends_table()
        try:
            # Updated query to use 'username' instead of 'user'
            response = table.query(
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={
                    ':username': username
                }
            )
            return [item['friend'] for item in response.get('Items', [])]
        except ClientError as e:
            print(f"Error getting friends: {e.response['Error']['Message']}")
            return []
        

    @staticmethod
    def get_sent_requests(user):
        table = FriendRequest.get_friend_requests_table()
        try:
            response = table.query(
                IndexName='from_user-index',
                KeyConditionExpression='from_user = :user',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':user': user, ':status': 'pending'}
            )
            return response['Items']
        except ClientError as e:
            print(e.response['Error']['Message'])
            return []