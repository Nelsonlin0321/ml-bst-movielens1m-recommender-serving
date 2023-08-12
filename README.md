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


## Run Recommender API Locally


```sh
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install torch --index-url https://download.pytorch.org/whl/cpu

source .env
uvicorn server:app --reload-dir src --host 0.0.0.0 --port 8000
```

## Run Recommender API Using Docker

### Build the docker
```sh
docker build -t bst-movielens1m-recommender-serving:latest . --platform linux/arm64/v8
```

### Run Docker Container
```sh
docker run --env-file docker.env -p 5050:5050 -it bst-movielens1m-recommender-serving:latest
```
or
```sh
docker compose up
```

## Call The API

fastapi docs swagger for information: the http://0.0.0.0:8000/docs

```sh
curl -X 'POST' \
  'http://0.0.0.0:8000/recommend' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "movie_ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "user_age": 20,
  "sex": "M",
  "topk": 3
}'
```

## Build AWS Lambda FastAPI Container

```sh
docker build -t movielens1m-recommender-lambda:latest -f ./Dockerfile.aws.lambda  . --platform linux/arm64/v8
```

## Test the Lambda
```sh
docker run --env-file docker.env -p 9000:8080 --name lambda-recommender -it movielens1m-recommender-lambda:latest
```

```sh
# TEST healthcheck
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
    "resource": "/healthcheck",
    "path": "/healthcheck",
    "httpMethod": "GET",
    "requestContext": {
    },
    "isBase64Encoded": false
}'

# OUTPUT
# {"statusCode": 200, "headers": {"content-length": "95", "content-type": "application/json"}, "multiValueHeaders": {}, "body": "{\"message\":\"The server is up since 2023-08-12 03:57:28\",\"start_uct_time\":\"2023-08-12 03:57:28\"}", "isBase64Encoded": false}% 

# TEST Recommend Endpoint
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
    "resource": "/recommend",
    "path": "/recommend",
    "httpMethod": "POST",
    "requestContext": {
        "resourcePath": "/recommend",
        "httpMethod": "POST"
    },
    "body": "{\"movie_ids\": [1, 2, 3, 4], \"user_age\": 23, \"sex\": \"M\", \"topk\": 1}",
    "isBase64Encoded": false
}'

#OUTPUT
# {"statusCode": 200, "headers": {"content-length": "154", "content-type": "application/json"}, "multiValueHeaders": {}, "body": "[{\"movie_id\":50,\"title\":\"Usual Suspects, The (1995)\",\"genres\":[\"Crime\",\"Thriller\"],\"release_year\":1995,\"origin_title\":\"Usual Suspects, The\",\"rating\":5.0}]", "isBase64Encoded": false}% 
```