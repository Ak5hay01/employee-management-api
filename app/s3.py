import boto3

from app.config import S3_BUCKET_NAME, AWS_REGION


s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_image(
    file_content,
    object_key,
    content_type
):
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=object_key,
        Body=file_content,
        ContentType=content_type
    )


def delete_image(object_key):

    if not object_key:
        return

    s3_client.delete_object(
        Bucket=S3_BUCKET_NAME,
        Key=object_key
    )


def generate_presigned_url(
    object_key,
    expiration=3600
):

    if not object_key:
        return None

    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": object_key
        },
        ExpiresIn=expiration
    )