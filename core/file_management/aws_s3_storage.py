from __future__ import annotations

from typing import Union, List, Dict, Any

from .storage_interface import StorageInterface

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None

class S3Storage(StorageInterface):
    """
    Implementation of storage on AWS S3.
    """
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, region_name=None):
        if not boto3:
            raise ImportError("boto3 is required for S3 storage.")
        
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.bucket_name = bucket_name

    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        key = self._get_safe_path(filename, path_dir)
        
        # Determine ACL
        acl = 'public-read' if visibility == 'public' else 'private'
        
        try:
            # Check if file is a file-like object or bytes
            if hasattr(file, 'read'):
                file.seek(0)
                data = file.read()
            else:
                data = file

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ACL=acl,
                Metadata={
                    'access_rights': access_rights,
                    'created_at': self._now()
                }
            )
            
            # Construct metadata
            metadata = {
                "filename": filename,
                "path": key,
                "created_at": self._now(),
                "modified_at": self._now(),
                "access_rights": access_rights,
                "visibility": visibility,
                "size": len(data) if isinstance(data, bytes) else 0, # Approximation if not bytes
                "backend": "s3",
                "url": f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            }
            return metadata
        except ClientError as e:
            print(f"S3 Error: {e}")
            return False

    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        key = self._get_safe_path(filename, path_dir)
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise FileNotFoundError(f"S3 File {key} not found: {e}")

    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        key = self._get_safe_path(filename, path_dir)
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return {
                "filename": filename,
                "path": key,
                "modified_at": response.get('LastModified').isoformat() if response.get('LastModified') else None,
                "size": response.get('ContentLength'),
                "content_type": response.get('ContentType'),
                "backend": "s3",
                "custom_metadata": response.get('Metadata', {})
            }
        except ClientError as e:
            raise FileNotFoundError(f"S3 Metadata for {key} not found: {e}")

    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        # S3 update is essentially an overwrite
        result = self.save(new_file, filename, path_dir)
        return bool(result)

    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        key = self._get_safe_path(filename, path_dir)
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
