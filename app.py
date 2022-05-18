import os
import json
import boto3
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


dynamodb_client = boto3.client('dynamodb')
iam_client = boto3.client('iam')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )

USERS_TABLE = os.environ['USERS_TABLE']


@app.route('/user/<string:userName>')
def get_user(userName):
    result = dynamodb_client.get_item(
        TableName=USERS_TABLE, Key={'name': {'S': userName}}
    )
    item = result.get('Item')
    if not items:
        return jsonify({'error': 'Could not find user with provided "userId"'}), 404

    return jsonify(
        {'userId': item.get('userId').get('S'), 'name': item.get('name').get('S')}
    )
 
@app.route('/users')
def list_users():
    response = dynamodb_client.scan(TableName=USERS_TABLE)
    items = response['Items']
    # Prints All the Items at once
    if not items:
        return jsonify({'error': 'Could not find users'}), 404
        
    return json.dumps(items)
       
    
@app.route('/sync')
def sync_users():
    iamUsers = iam_client.list_users()
    user_names= [ iamUser['UserName'] for iamUser in iamUsers['Users'] ]
    dynamodb = boto3.resource('dynamodb')
    table=dynamodb.Table(USERS_TABLE)
    response = table.scan(ProjectionExpression = 'userId,#c',
                      ExpressionAttributeNames = {'#c': 'name'})
    items = response['Items']
    for key in iamUsers['Users']:
            dynamodb_client.put_item(
            TableName=USERS_TABLE, Item={'userId': {'S': key['UserId']}, 'name': {'S': key['UserName']}}
            )
    for item in items:
        if item['name'] not in user_names:
            dynamodb_client.delete_item(
            TableName=USERS_TABLE,Key={'userId': {'S': item['userId']}}
            )
    return jsonify("Users synced")
    

@app.route('/users', methods=['POST'])
def create_user():
    data= json.loads(request.data.decode('utf-8'))
    userName = data['name']
    if not userName:
        return jsonify({'error': 'Please provide "Username"'}), 400
    response = iam_client.create_user(
    UserName=userName,
    PermissionsBoundary='arn:aws:iam::aws:policy/AdministratorAccess'
    )
    sync_users()
    return jsonify({'CreatedUser': userName})

@app.route('/users', methods=['DELETE'])
def delete_user():
    data= json.loads(request.data.decode('utf-8'))
    userName = data['name']
    if not userName:
        return jsonify({'error': 'Please provide "Username"'}), 400
    response = iam_client.delete_user(
    UserName=userName
    )
    sync_users()
    return jsonify({'DeletedUser': userName})
    

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
