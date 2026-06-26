"""Input validation utilities."""

import logging
from pathlib import Path
from typing import Tuple, Optional
import mimetypefrom config import SUPPORTED_FORMATS, MAX_UPLOAD_SIZE

logger = logging.getLogger(__name__)


def validate_image_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate image file for analysis.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    try:
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > MAX_UPLOAD_SIZE:
            return False, f"File size {file_size} exceeds maximum {MAX_UPLOAD_SIZE}"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Check file format
        suffix = path.suffix.lower().strip('.')
        if suffix not in SUPPORTED_FORMATS:
            return False, f"Unsupported format: {suffix}. Supported: {SUPPORTED_FORMATS}"
        
        logger.info(f"Image validation passed: {file_path} ({file_size} bytes)")
        return True, "Valid"
        
    except Exception as e:
        logger.error(f"Error validating image: {e}")
        return False, f"Validation error: {str(e)}"


def validate_image_dimensions(file_path: str) -> Tuple[bool, str]:
    """
    Validate image has reasonable dimensions.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    try:
        from PIL import Image
        img = Image.open(file_path)
        width, height = img.size
        
        min_dimension = 32
        max_dimension = 65536
        
        if width < min_dimension or height < min_dimension:
            return False, f"Image too small: {width}x{height}"
        
        if width > max_dimension or height > max_dimension:
            return False, f"Image too large: {width}x{height}"
        
        # Check aspect ratio (not extreme)
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 10:
            return False, f"Image aspect ratio too extreme: {aspect_ratio:.1f}:1"
        
        logger.info(f"Dimension validation passed: {width}x{height}")
        return True, "Valid"
        
    except Exception as e:
        logger.error(f"Error validating dimensions: {e}")
        return False, f"Dimension validation error: {str(e)}"


def validate_image_corruption(file_path: str) -> Tuple[bool, str]:
    """
    Validate image file is not corrupted.
    
    Args:
        file_path: Path to image file
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    try:
        from PIL import Image
        img = Image.open(file_path)
        img.verify()
        logger.info(f"Corruption check passed: {file_path}")
        return True, "Valid"
    except Exception as e:
        logger.error(f"Image corruption detected: {e}")
        return False, f"Image appears corrupted: {str(e)}"


def validate_all_image_checks(file_path: str) -> Tuple[bool, str]:
    """
    Run all validation checks on image.
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    checks = [
        validate_image_file,
        validate_image_dimensions,
        validate_image_corruption,
    ]
    
    for check in checks:
        is_valid, message = check(file_path)
        if not is_valid:
            return False, f"{check.__name__}: {message}"
    
    return True, "All validations passed"


def validate_case_info(case_info: dict) -> Tuple[bool, str]:
    """
    Validate case metadata.
    
    Args:
        case_info: Dictionary with case information
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    required_fields = ["case_number", "case_name"]
    
    for field in required_fields:
        if field not in case_info or not case_info[field]:
            return False, f"Missing required field: {field}"
    
    # Validate case number format
    case_number = str(case_info.get("case_number", "")).strip()
    if len(case_number) < 3:
        return False, "Case number too short"
    
    # Validate case name length
    case_name = str(case_info.get("case_name", "")).strip()
    if len(case_name) < 3 or len(case_name) > 200:
        return False, "Case name must be 3-200 characters"
    
    return True, "Valid"
