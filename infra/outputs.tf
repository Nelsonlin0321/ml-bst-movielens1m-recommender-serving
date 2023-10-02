output "apigateway_invoke_url" {
  value = aws_api_gateway_deployment.lambda_rest_prod_gateway.invoke_url
}