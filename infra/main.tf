terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.18"
    }
  }

  required_version = ">= 1.2.0"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.lambda_function_name}-iam-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
}


data "aws_iam_policy_document" "lambda_logging" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_logging_policy" {
  name        = "${var.lambda_function_name}_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.lambda_logging.json
}


resource "aws_iam_role_policy_attachment" "lambda_logs_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}

data "aws_iam_policy_document" "lambda_s3_access" {
  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = ["arn:aws:s3:::s3-mlflow-artifacts-storage/*",
    "arn:aws:s3:::s3-mlflow-artifacts-storage"]
  }
}

resource "aws_iam_policy" "lambda_s3_access_policy" {
  name        = "${var.lambda_function_name}_lambda_s3_access"
  path        = "/"
  description = "IAM policy of s3 access for lambda ${var.lambda_function_name}"
  policy      = data.aws_iam_policy_document.lambda_s3_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access_policy_attachment" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_s3_access_policy.arn
}


resource "aws_lambda_function" "movielens1m_recommender_lambda" {
  function_name = var.lambda_function_name

  timeout      = 5
  memory_size  = 720
  image_uri     = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/${var.ecr_repository_name}:latest"
  package_type  = "Image"
  architectures = ["x86_64"]
  depends_on = [
    aws_cloudwatch_log_group.lambda_log_group,
    aws_iam_role_policy_attachment.lambda_logs_policy_attachment,
    aws_iam_role_policy_attachment.lambda_s3_access_policy_attachment
    
  ]
  role = aws_iam_role.iam_for_lambda.arn

  ephemeral_storage {
    size = 512
  }

  environment {
    variables = {
      ARTIFACTS_URL = var.ARTIFACTS_URL
      BATCH_SIZE = var.BATCH_SIZE
    }
  }
}


resource "aws_api_gateway_rest_api" "lambda_rest_gateway" {
  name = "${var.lambda_function_name}-api"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  parent_id   = "${aws_api_gateway_rest_api.lambda_rest_gateway.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  resource_id   = "${aws_api_gateway_resource.proxy.id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.movielens1m_recommender_lambda.invoke_arn}"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.lambda_rest_gateway.execution_arn}/*/*"
}


resource "aws_api_gateway_deployment" "lambda_rest_prod_gateway" {
  depends_on = [
    aws_api_gateway_integration.lambda,
  ]

  rest_api_id = "${aws_api_gateway_rest_api.lambda_rest_gateway.id}"
  stage_name  = "prod"
}
