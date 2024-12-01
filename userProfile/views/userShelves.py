from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import boto3
import os
from boto3.dynamodb.conditions import Attr

@login_required
def user_shelves(request):
    # Fetch games data from DynamoDB
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    table = dynamodb.Table('user-shelves')
    filter_expression = Attr('user_id').eq(request.user.username)
    scan_params = {
        'FilterExpression': filter_expression,
    }
    response = table.scan(**scan_params)

    # Organize games into tabs
    tabs = ["playing", "completed", "abandoned", "paused", "want-to-play"]
    user_games = {tab: response['Items'][0].get(tab, []) for tab in tabs}

    return render(request, 'userShelves.html', {'user_games': user_games, 'tabs': tabs})