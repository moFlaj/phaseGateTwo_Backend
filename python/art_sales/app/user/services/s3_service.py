# app/artist/services/s3_service.py
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime, UTC
from app.user.services.image_cache_service import image_cache


class S3Service:
    """Encapsulates all S3-related operations (upload + download)."""

    def __init__(self):
        self.bucket = os.getenv("AWS_S3_BUCKET", "test-bucket")
        self.region = os.getenv("AWS_S3_REGION", "us-east-1")
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test-key"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test-secret"),
        )

    def generate_upload_url(self, filename: str, content_type: str = "image/jpeg") -> dict:
        """
        Generate a presigned PUT URL for direct upload to S3.
        Returns both the upload URL and the key (used to retrieve later).
        """
        key = f"artworks/{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{filename}"
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=3600,
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to generate signed upload URL: {e}")

        # Also generate the final URL that can be used to access the uploaded file
        final_url = self.generate_get_url(key, expires_in=86400)  # 24 hours
        
        return {"upload_url": presigned_url, "key": key, "final_url": final_url}

    def generate_get_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned GET URL for temporary access to a private object.
        Uses caching to avoid regenerating URLs for recently requested images.
        """
        # Check cache first
        cached_url = image_cache.get(key)
        if cached_url:
            return cached_url
            
        # Generate new URL
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to generate signed GET URL: {e}")
            
        # Cache the URL
        image_cache.set(key, url, expires_in)
        return url