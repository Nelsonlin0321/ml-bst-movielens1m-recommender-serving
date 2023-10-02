variable "region" {
  default = "ap-southeast-1"
}

variable "account_id" {
  default = "932682266260"
}

variable "lambda_function_name" {
  default = "movielens1m-transformer-based-recommender-lambda"
}


variable "ecr_repository_name" {
  default = "movielens1m-recommender-lambda"
}

variable "ARTIFACTS_URL" {
  default = "s3://s3-mlflow-artifacts-storage/mlflow/15/7008c7131367497a8dd99e2b2d506f96"
}

variable "BATCH_SIZE" {
  default = "12"
}


