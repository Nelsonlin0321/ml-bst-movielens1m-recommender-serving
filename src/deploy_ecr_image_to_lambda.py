import argparse

import boto3

parser = argparse.ArgumentParser(
    description='utils to deploy to ecr image url to lambda')

parser.add_argument('--repository_name', type=str, required=True,
                    default="movielens1m-recommender-lambda")

parser.add_argument('--image_tag', type=str, required=True,
                    default="latest")

parser.add_argument('--function_name', type=str, required=True,
                    default="movielens1m-recommender-lambda")

# pylint:disable=redefined-outer-name,invalid-name,broad-exception-raised


def get_image_url(repository_name="movielens1m-recommender-lambda", image_tag="latest"):

    ecr_client = boto3.client('ecr')

    response = ecr_client.describe_repositories(
        repositoryNames=[repository_name])
    repositoryUri = response['repositories'][0]['repositoryUri']

    response = ecr_client.describe_images(
        repositoryName=repository_name,
        imageIds=[
            {
                'imageTag': image_tag
            }
        ]
    )

    imageDigest = response['imageDetails'][0]['imageDigest']

    latest_image_url = "@".join([repositoryUri, imageDigest])

    return latest_image_url


def deploy_image_to_lambda(function_name, image_url):
    lambda_client = boto3.client('lambda')
    response = lambda_client.update_function_code(
        FunctionName=function_name,
        ImageUri=image_url
    )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(response)

    print(f"Deploy To Lambda Successfully With Image URL: {image_url}!")


if __name__ == "__main__":

    args = parser.parse_args()
    repository_name = args.repository_name
    image_tag = args.image_tag
    function_name = args.function_name

    latest_image_url = get_image_url(repository_name, image_tag)
    deploy_image_to_lambda(function_name, latest_image_url)
