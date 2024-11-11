from django.conf import settings
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime
from django.contrib.auth import get_user_model

class FriendRequest:
    @staticmethod
    def get_dynamodb_resource():
        try:
            return boto3.resource(
                'dynamodb',
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                region_name='us-east-1'
            )
        except Exception as e:
            print(f"Error connecting to DynamoDB: {e}")
            return None

    @staticmethod
    def ensure_tables_exist():
        try:
            dynamodb = boto3.client(
                'dynamodb',
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                region_name='us-east-1'
            )
            
            # Check and create friend_requests table
            try:
                dynamodb.describe_table(TableName='friend_requests')
            except dynamodb.exceptions.ResourceNotFoundException:
                dynamodb.create_table(
                    TableName='friend_requests',
                    KeySchema=[
                        {'AttributeName': 'to_user', 'KeyType': 'HASH'},
                        {'AttributeName': 'from_user', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'to_user', 'AttributeType': 'S'},
                        {'AttributeName': 'from_user', 'AttributeType': 'S'}
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': 'from_user-index',
                            'KeySchema': [
                                {'AttributeName': 'from_user', 'KeyType': 'HASH'},
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL'
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 5,
                                'WriteCapacityUnits': 5
                            }
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                
            # Check and create user_friends table
            try:
                dynamodb.describe_table(TableName='user_friends')
            except dynamodb.exceptions.ResourceNotFoundException:
                dynamodb.create_table(
                    TableName='user_friends',
                    KeySchema=[
                        {'AttributeName': 'username', 'KeyType': 'HASH'},
                        {'AttributeName': 'friend', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'username', 'AttributeType': 'S'},
                        {'AttributeName': 'friend', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
            return True
        except Exception as e:
            print(f"Error ensuring tables exist: {e}")
            return False

    @staticmethod
    def get_friend_requests_table():
        FriendRequest.ensure_tables_exist()  # First ensure tables exist
        dynamodb = FriendRequest.get_dynamodb_resource()
        return dynamodb.Table('friend_requests')

    @staticmethod
    def get_friends_table():
        try:
            dynamodb = FriendRequest.get_dynamodb_resource()
            if not dynamodb:
                raise Exception("Could not connect to DynamoDB")
            
            table = dynamodb.Table('user_friends')
            # Test if table is accessible
            table.table_status
            return table
        except Exception as e:
            print(f"Error getting friends table: {e}")
            # Try to create tables if they don't exist
            from .utils import create_dynamodb_tables
            create_dynamodb_tables()
            # Try one more time
            try:
                return dynamodb.Table('user_friends')
            except Exception as e:
                print(f"Final error getting friends table: {e}")
                return None

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
    def get_pending_requests(username):
        table = FriendRequest.get_friend_requests_table()
        if not table:
            return []
        
        try:
            response = table.query(
                KeyConditionExpression='to_user = :username',
                ExpressionAttributeValues={
                    ':username': username
                }
            )
            return response.get('Items', [])
        except Exception as e:
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
            # The key in DynamoDB must match how it was stored
            # When a request is sent, it's stored with to_user and from_user
            table.delete_item(
                Key={
                    'to_user': to_user,
                    'from_user': from_user
                }
            )
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    @staticmethod
    def get_friends(username):
        print(f"Getting friends for {username}")  # Debug print
        table = FriendRequest.get_friends_table()
        if not table:
            print("Could not access friends table")
            return []
        
        try:
            response = table.query(
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={
                    ':username': username
                }
            )
            # Get friend usernames
            friend_usernames = [item['friend'] for item in response.get('Items', [])]
            
            # Get user IDs for each friend
            from django.contrib.auth import get_user_model
            User = get_user_model()
            friends_with_ids = []
            for friend_username in friend_usernames:
                try:
                    friend = User.objects.get(username=friend_username)
                    friends_with_ids.append({
                        'username': friend_username,
                        'user_id': friend.id  # Changed from 'id' to 'user_id' to match template
                    })
                except User.DoesNotExist:
                    continue
            
            return friends_with_ids
        except Exception as e:
            print(f"Error getting friends: {e}")
            return []
        

    @staticmethod
    def get_sent_requests(username):
        table = FriendRequest.get_friend_requests_table()
        if not table:
            return []
        
        try:
            response = table.query(
                IndexName='from_user-index',
                KeyConditionExpression='from_user = :username',
                ExpressionAttributeValues={
                    ':username': username
                }
            )
            return response.get('Items', [])
        except Exception as e:
            return []

    @staticmethod
    def get_user_info(username):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            return {
                'id': user.id,
                'username': user.username
            }
        except User.DoesNotExist:
            return None

    @staticmethod
    def cancel_request(from_user, to_user):
        table = FriendRequest.get_friend_requests_table()
        try:
            table.delete_item(
                Key={
                    'to_user': to_user,
                    'from_user': from_user
                }
            )
            return True
        except ClientError as e:
            print(f"Error cancelling friend request: {e.response['Error']['Message']}")
            return False

    @staticmethod
    def remove_friend(user1, user2):
        friends_table = FriendRequest.get_friends_table()
        try:
            # Remove from first user's friends
            friends_table.delete_item(
                Key={
                    'username': user1,
                    'friend': user2
                }
            )
            
            # Remove from second user's friends
            friends_table.delete_item(
                Key={
                    'username': user2,
                    'friend': user1
                }
            )
            return True
        except ClientError as e:
            print(f"Error removing friend: {e.response['Error']['Message']}")
            return False