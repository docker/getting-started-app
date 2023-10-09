provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    dynamodb = "http://localhost:4566"
    apigateway = "http://localhost:4566"
    lambda = "http://localhost:4574"
  }
}

resource "aws_dynamodb_table" "example" {
  name           = "example"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "ID"

  attribute {
    name = "ID"
    type = "N"
  }
}

resource "aws_api_gateway_rest_api" "gateway" {
  name        = "gateway"
  description = "This is my API for demonstration purposes"
}

resource "aws_api_gateway_resource" "gatewayResource" {
  rest_api_id = aws_api_gateway_rest_api.gateway.id
  parent_id   = aws_api_gateway_rest_api.gateway.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "gatewayMethod" {
  rest_api_id   = aws_api_gateway_rest_api.gateway.id
  resource_id   = aws_api_gateway_resource.gatewayResource.id
  http_method   = "POST"
  authorization = "NONE"
}