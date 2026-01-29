# Supabase Storage service
# Handles file upload, download, and signed URL generation

from typing import Optional
from supabase import Client
from .supabase_client import get_client


class StorageError(Exception):
    """Custom exception for storage operations"""
    pass


def upload_bytes(
    bucket: str,
    path: str,
    content_bytes: bytes,
    content_type: str = "application/octet-stream"
) -> str:
    """
    Upload bytes to Supabase Storage.
    
    Args:
        bucket: Storage bucket name (e.g., 'uploads', 'outputs')
        path: File path within the bucket (e.g., 'run_id/file.xlsx')
        content_bytes: File content as bytes
        content_type: MIME type (default: 'application/octet-stream')
        
    Returns:
        str: Path to uploaded file
        
    Raises:
        StorageError: If upload fails
    """
    try:
        client: Client = get_client()
        
        # Upload to Supabase Storage
        response = client.storage.from_(bucket).upload(
            path=path,
            file=content_bytes,
            file_options={
                "content-type": content_type,
                "upsert": "true"  # Allow overwriting existing files
            }
        )
        
        # Check for errors in response
        if hasattr(response, 'error') and response.error:
            raise StorageError(f"Upload failed: {response.error}")
        
        return path
        
    except StorageError:
        raise
    except Exception as e:
        raise StorageError(f"Failed to upload file to {bucket}/{path}: {str(e)}")


def download_bytes(bucket: str, path: str) -> bytes:
    """
    Download file from Supabase Storage as bytes.
    
    Args:
        bucket: Storage bucket name (e.g., 'uploads', 'outputs')
        path: File path within the bucket
        
    Returns:
        bytes: File content
        
    Raises:
        StorageError: If download fails or file not found
    """
    try:
        client: Client = get_client()
        
        # Download from Supabase Storage
        response = client.storage.from_(bucket).download(path)
        
        if response is None:
            raise StorageError(f"File not found: {bucket}/{path}")
        
        return response
        
    except StorageError:
        raise
    except Exception as e:
        raise StorageError(f"Failed to download file from {bucket}/{path}: {str(e)}")


def create_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    """
    Generate a signed URL for temporary file access.
    
    Args:
        bucket: Storage bucket name (e.g., 'uploads', 'outputs')
        path: File path within the bucket
        expires_in: URL expiration time in seconds (default: 3600 = 1 hour)
        
    Returns:
        str: Signed URL for file download
        
    Raises:
        StorageError: If URL generation fails
    """
    try:
        client: Client = get_client()
        
        # Create signed URL
        response = client.storage.from_(bucket).create_signed_url(
            path=path,
            expires_in=expires_in
        )
        
        if not response or 'signedURL' not in response:
            raise StorageError(f"Failed to create signed URL for {bucket}/{path}")
        
        return response['signedURL']
        
    except StorageError:
        raise
    except Exception as e:
        raise StorageError(f"Failed to create signed URL for {bucket}/{path}: {str(e)}")


def delete_file(bucket: str, path: str) -> None:
    """
    Delete a file from Supabase Storage.
    
    Args:
        bucket: Storage bucket name
        path: File path within the bucket
        
    Raises:
        StorageError: If deletion fails
    """
    try:
        client: Client = get_client()
        
        response = client.storage.from_(bucket).remove([path])
        
        if hasattr(response, 'error') and response.error:
            raise StorageError(f"Delete failed: {response.error}")
            
    except StorageError:
        raise
    except Exception as e:
        raise StorageError(f"Failed to delete file {bucket}/{path}: {str(e)}")


def get_public_url(bucket: str, path: str) -> str:
    """
    Get public URL for a file (if bucket is public).
    
    Args:
        bucket: Storage bucket name
        path: File path within the bucket
        
    Returns:
        str: Public URL
        
    Raises:
        StorageError: If URL generation fails
    """
    try:
        client: Client = get_client()
        
        response = client.storage.from_(bucket).get_public_url(path)
        
        if not response:
            raise StorageError(f"Failed to get public URL for {bucket}/{path}")
        
        return response
        
    except StorageError:
        raise
    except Exception as e:
        raise StorageError(f"Failed to get public URL for {bucket}/{path}: {str(e)}")


