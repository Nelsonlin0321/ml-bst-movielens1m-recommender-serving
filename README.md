# Movielens 1m Movie Recommendation Serving Based on Behavior Sequence Transformer Model 

## Environmenet Settings

.env file

AWS Secrets are used to download s3 artifacts.
You can use the repository artifacts but you have to remove "artifacts" from .dockerignore 

```sh
export AWS_DEFAULT_REGION=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export ARTIFACTS_URL=s3://s3-mlflow-artifacts-storage/mlflow/15/7008c7131367497a8dd99e2b2d506f96
export PORT=5050
export WORKERS=2
export THREADS=2
```

## Build AWS Lambda FastAPI Container

```sh
docker build -t movielens1m-recommender-lambda:latest -f ./Dockerfile  . --platform linux/arm64/v8
```

## Test the Lambda
```sh
docker run --env-file docker.env -p 9000:8080 --name lambda-recommender --rm -it movielens1m-recommender-lambda:latest
```

```sh
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"payload":"hello world!"}'
```




## Debug Container

```sh
docker exec -it lambda-recommender /bin/bash
```

## Push Image to ECR
```
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 932682266260.dkr.ecr.ap-southeast-1.amazonaws.com

docker tag bst-movielens1m-recommender-lambda-serving:latest 932682266260.dkr.ecr.ap-southeast-1.amazonaws.com/bst-movielens1m-recommender-lambda-serving:latest

```

```sh
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
  "resource": "/healthcheck",
  "payload":"hello world!"
  "httpMethod": "GET",
  "path": "/healthcheck",
  }'
```

```sh
curl -XPOST "http://localhost:8080/2015-03-31/functions/function/invocations" -d '{
    "resource": "/hello",
    "path": "/hello",
    "httpMethod": "GET",
    "headers": {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate",
      "cache-control": "no-cache",
      "CloudFront-Forwarded-Proto": "https",
      "CloudFront-Is-Desktop-Viewer": "true",
      "CloudFront-Is-Mobile-Viewer": "false",
      "CloudFront-Is-SmartTV-Viewer": "false",
      "CloudFront-Is-Tablet-Viewer": "false",
      "CloudFront-Viewer-Country": "US",
      "Content-Type": "application/json",
      "headerName": "headerValue",
      "Host": "gy415nuibc.execute-api.us-east-1.amazonaws.com",
      "Postman-Token": "9f583ef0-ed83-4a38-aef3-eb9ce3f7a57f",
      "User-Agent": "PostmanRuntime/2.4.5",
      "Via": "1.1 d98420743a69852491bbdea73f7680bd.cloudfront.net (CloudFront)",
      "X-Amz-Cf-Id": "pn-PWIJc6thYnZm5P0NMgOUglL1DYtl0gdeJky8tqsg8iS_sgsKD1A==",
      "X-Forwarded-For": "54.240.196.186, 54.182.214.83",
      "X-Forwarded-Port": "443",
      "X-Forwarded-Proto": "https"
    },
    "multiValueHeaders":{
      "Accept":[
        "*/*"
      ],
      "Accept-Encoding":[
        "gzip, deflate"
      ],
      "cache-control":[
        "no-cache"
      ],
      "CloudFront-Forwarded-Proto":[
        "https"
      ],
      "CloudFront-Is-Desktop-Viewer":[
        "true"
      ],
      "CloudFront-Is-Mobile-Viewer":[
        "false"
      ],
      "CloudFront-Is-SmartTV-Viewer":[
        "false"
      ],
      "CloudFront-Is-Tablet-Viewer":[
        "false"
      ],
      "CloudFront-Viewer-Country":[
        "US"
      ],
      "":[
        ""
      ],
      "Content-Type":[
        "application/json"
      ],
      "headerName":[
        "headerValue"
      ],
      "Host":[
        "gy415nuibc.execute-api.us-east-1.amazonaws.com"
      ],
      "Postman-Token":[
        "9f583ef0-ed83-4a38-aef3-eb9ce3f7a57f"
      ],
      "User-Agent":[
        "PostmanRuntime/2.4.5"
      ],
      "Via":[
        "1.1 d98420743a69852491bbdea73f7680bd.cloudfront.net (CloudFront)"
      ],
      "X-Amz-Cf-Id":[
        "pn-PWIJc6thYnZm5P0NMgOUglL1DYtl0gdeJky8tqsg8iS_sgsKD1A=="
      ],
      "X-Forwarded-For":[
        "54.240.196.186, 54.182.214.83"
      ],
      "X-Forwarded-Port":[
        "443"
      ],
      "X-Forwarded-Proto":[
        "https"
      ]
    },
    "queryStringParameters": {
    },
    "multiValueQueryStringParameters":{
    },
    "pathParameters": {
    },
    "stageVariables": {
      "stageVariableName": "stageVariableValue"
    },
    "requestContext": {
      "accountId": "12345678912",
      "resourceId": "roq9wj",
      "stage": "testStage",
      "requestId": "deef4878-7910-11e6-8f14-25afc3e9ae33",
      "identity": {
        "cognitoIdentityPoolId": null,
        "accountId": null,
        "cognitoIdentityId": null,
        "caller": null,
        "apiKey": null,
        "sourceIp": "192.168.196.186",
        "cognitoAuthenticationType": null,
        "cognitoAuthenticationProvider": null,
        "userArn": null,
        "userAgent": "PostmanRuntime/2.4.5",
        "user": null
      },
      "resourcePath": "/hello",
      "httpMethod": "GET",
      "apiId": "gy415nuibc"
    },
    "body": "{}",
    "isBase64Encoded": false
}'