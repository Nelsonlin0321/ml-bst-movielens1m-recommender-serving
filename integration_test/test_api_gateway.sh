curl -X 'POST' \
  'https://j87zs9ftf4.execute-api.ap-southeast-1.amazonaws.com/production/recommend' \
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
  "rating_threshold":4.8
}'