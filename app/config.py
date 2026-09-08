import os


S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

AWS_REGION = os.getenv(
    "AWS_DEFAULT_REGION",
    "us-east-1"
)