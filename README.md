
# Serverless Framework Python Flask API service backed by DynamoDB on AWS

This template demonstrates a simple Python Flask API service, backed by DynamoDB, running on AWS Lambda using the traditional Serverless Framework.


## Anatomy of the template

This template configures a single function, `api`, which is responsible for handling all incoming requests thanks to configured `httpApi` events. The implementation takes advantage of `serverless-wsgi`, which allows you to wrap WSGI applications such as Flask apps. The template also relies on `serverless-python-requirements` plugin for packaging dependencies from `requirements.txt` file. 

Additionally, the template also handles provisioning of a DynamoDB database that is used for storing data about IAM users. The Flask application exposes five endpoints, `POST /users`, `GET /user/{userId}`, `GET /users`,`DELETE /users`and `GET /sync` which allow to create, retrieve specific user , retrieve all users, delete users and sync iam users and dynamodb.

## Usage

### Prerequisites

In order to package your dependencies locally with `serverless-python-requirements`, you need to have `Python3.8` installed locally. You can create and activate a dedicated virtual environment with the following command:

```bash
npm install --save-dev serverless-wsgi serverless-python-requirements
virtualenv venv --python=python3
source venv/bin/activate
(venv) $ pip install flask
(venv) $ pip freeze > requirements.txt
```


### Deployment

```
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying aws-python-flask-dynamodb-api-project to stage dev (us-east-1)

✔ Service deployed to stack aws-python-flask-dynamodb-api-project-dev (182s)

endpoint: ANY - https://xxxxxxxx.execute-api.us-east-1.amazonaws.com
functions:
  api: aws-python-flask-dynamodb-api-project-dev-api (1.5 MB)
```

_Note_: In current form, after deployment, API is public and can be invoked by anyone.

### Invocation

After successful deployment, you can create a new user by calling the corresponding endpoint:

```bash
curl --request POST 'https://xxxxxx.execute-api.us-east-1.amazonaws.com/users' --header 'Content-Type: application/json' --data-raw '{"name": "John" }'
```



You can later retrieve the user by `userName` by calling the following endpoint:

```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/users/userName
```
Which should result in the following response:

```bash
{"CREATED USER": userName}
```


You can later retrieve all the iam users by calling the following endpoint:

```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/users
```
Which should result in the list of users as json objects 


You can Sync all the iam users into dynamoDB by calling the following endpoint:

```bash
curl https://xxxxxxx.execute-api.us-east-1.amazonaws.com/sync
```
Which should result in the following response:

```bash
USERS SYNCED
```


You can later delete  the iam use by `userName` by calling the following endpoint:

```bash
curl --request DELETE 'https://xxxxxx.execute-api.us-east-1.amazonaws.com/users' --header 'Content-Type: application/json' --data-raw '{"name": "John" }'
```
Which should result in the following response:

```bash
{"DELETED USER": userName}
```


### Local development

Thanks to capabilities of `serverless-wsgi`, it is also possible to run your application locally, however, in order to do that, you will need to first install `werkzeug`, `boto3` dependencies, as well as all other dependencies listed in `requirements.txt`. It is recommended to use a dedicated virtual environment for that purpose. You can install all needed dependencies with the following commands:

```bash
pip install werkzeug boto3
pip install -r requirements.txt
```

Additionally, you will need to emulate DynamoDB locally, which can be done by using `serverless-dynamodb-local` plugin. In order to do that, execute the following commands:

```bash
serverless plugin install -n serverless-dynamodb-local
serverless dynamodb install
```

It will add the plugin to `devDependencies` in `package.json` file as well as to `plugins` section in `serverless.yml`. Additionally, it will also install DynamoDB locally.

You should also add the following config to `custom` section in `serverless.yml`:


```yml
custom:
  (...)
  dynamodb:
    start:
      migrate: true
    stages:
      - dev
```

Additionally, we need to reconfigure DynamoDB Client to connect to our local instance of DynamoDB. We can take advantage of `IS_OFFLINE` environment variable set by `serverless-wsgi` plugin and replace:


```python
dynamodb_client = boto3.client('dynamodb')
```

with

```python
dynamodb_client = boto3.client('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client('dynamodb', region_name='localhost', endpoint_url='http://localhost:8000')
```

Now you can start DynamoDB local with the following command:

```bash
serverless dynamodb start
```

At this point, you can run your application locally with the following command:

```bash
serverless wsgi serve
```

For additional local development capabilities of `serverless-wsgi` and `serverless-dynamodb-local` plugins, please refer to corresponding GitHub repositories:
- https://github.com/logandk/serverless-wsgi 
- https://github.com/99x/serverless-dynamodb-local
# slsapis
