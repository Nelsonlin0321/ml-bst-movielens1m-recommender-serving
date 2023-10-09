#!/usr/bin/env bash

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
    "resource": "/healthcheck",
    "path": "/healthcheck",
    "httpMethod": "GET",
    "requestContext": {
    },
    "isBase64Encoded": false
}'

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
    "resource": "/recommend",
    "path": "/recommend",
    "httpMethod": "POST",
    "requestContext": {
        "resourcePath": "/recommend",
        "httpMethod": "POST"
    },
    "body": "{\"movie_ids\": [1, 2, 3, 4], \"user_age\": 23, \"sex\": \"M\", \"topk\": 1, \"rating_threshold\": 4.8}",
    "isBase64Encoded": false
}'