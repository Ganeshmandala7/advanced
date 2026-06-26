"""Hash utilities for chain of custody."""

import hashlib
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def compute_sha256(file_path: str) -> str:
    """
    Compute SHA-256 hash of a file.
    
    Critical for chain of custody: compute BEFORE any processing touches the image.
    
    Args:
        file_path: Path to file
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        hash_value = sha256_hash.hexdigest()
        logger.info(f"Computed SHA-256 for {file_path}: {hash_value[:16]}...")
        return hash_value
    except Exception as e:
        logger.error(f"Error computing SHA-256: {e}")
        return ""


def verify_sha256(file_path: str, expected_hash: str) -> bool:
    """
    Verify file SHA-256 hash matches expected value.
    
    Args:
        file_path: Path to file
        expected_hash: Expected SHA-256 hash
        
    Returns:
        True if hash matches, False otherwise
    """
    computed = compute_sha256(file_path)
    result = computed == expected_hash
    if result:
        logger.info(f"SHA-256 verification passed for {file_path}")
    else:
        logger.warning(f"SHA-256 verification FAILED for {file_path}")
    return result


def compute_md5(file_path: str) -> str:
    """Compute MD5 hash (for reference, not cryptographic)."""
    try:
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)
        return md5_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error computing MD5: {e}")
        return ""


def generate_report_id() -> str:
    """
    Generate unique report ID in format: FX-YYYY-NNNN
    where YYYY is year and NNNN is sequential number.
    """
    from datetime import datetime
    import random
    year = datetime.now().year
    seq = random.randint(1000, 9999)
    return f"FX-{year}-{seq}"


def format_hash_for_display(hash_value: str, chars: int = 16) -> str:
    """Format hash for display (show first and last portion)."""
    if len(hash_value) <= chars * 2:
        return hash_value
    return f"{hash_value[:chars]}...{hash_value[-chars:]}"
